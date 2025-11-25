/**
 * CacheManager Service
 * Multi-layer caching strategy with TTL support and LRU eviction
 * Layers: request (5min), session (1hr), global (1 week), translation (1 week)
 */

export interface CacheEntry<T> {
  value: T;
  expiresAt: number;
  createdAt: number;
  hits: number;
}

export interface CacheConfig {
  maxSize: number;
  defaultTtl: number; // milliseconds
}

/**
 * Single-layer cache with TTL and LRU eviction
 */
class CacheLayer<T> {
  private cache: Map<string, CacheEntry<T>> = new Map();
  private maxSize: number;
  private defaultTtl: number;

  constructor(config: CacheConfig) {
    this.maxSize = config.maxSize;
    this.defaultTtl = config.defaultTtl;
  }

  /**
   * Get value from cache if not expired
   */
  get(key: string): T | undefined {
    const entry = this.cache.get(key);

    if (!entry) {
      return undefined;
    }

    // Check if expired
    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return undefined;
    }

    // Update hit count for LRU
    entry.hits += 1;
    return entry.value;
  }

  /**
   * Set value in cache with optional TTL override
   */
  set(key: string, value: T, ttl?: number): void {
    const now = Date.now();
    const ttlMs = ttl ?? this.defaultTtl;

    // If cache is full, evict least recently used entry
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      this.evictLRU();
    }

    this.cache.set(key, {
      value,
      expiresAt: now + ttlMs,
      createdAt: now,
      hits: 0,
    });
  }

  /**
   * Delete specific key
   */
  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  /**
   * Clear all entries in this layer
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics for monitoring
   */
  getStats(): {
    size: number;
    maxSize: number;
    oldestEntry: number | null;
    newestEntry: number | null;
  } {
    let oldestEntry: number | null = null;
    let newestEntry: number | null = null;

    for (const entry of this.cache.values()) {
      if (oldestEntry === null || entry.createdAt < oldestEntry) {
        oldestEntry = entry.createdAt;
      }
      if (newestEntry === null || entry.createdAt > newestEntry) {
        newestEntry = entry.createdAt;
      }
    }

    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      oldestEntry,
      newestEntry,
    };
  }

  /**
   * Evict least recently used entry based on hits and creation time
   */
  private evictLRU(): void {
    let lruKey: string | null = null;
    let lruScore = Infinity;

    for (const [key, entry] of this.cache.entries()) {
      // Score = hits + age (days). Lower hits and older = higher score (candidate for eviction)
      const ageMs = Date.now() - entry.createdAt;
      const ageDays = ageMs / (1000 * 60 * 60 * 24);
      const score = entry.hits + ageDays;

      if (score < lruScore) {
        lruScore = score;
        lruKey = key;
      }
    }

    if (lruKey !== null) {
      this.cache.delete(lruKey);
    }
  }
}

/**
 * Multi-layer cache manager for the application
 * Manages 4 cache layers with different TTLs:
 * - request: 5 minutes (for deduplication within single request)
 * - session: 1 hour (per-user session data)
 * - global: 1 week (shared across all sessions)
 * - translation: 1 week (translation results)
 */
export class CacheManager {
  private requestCache: CacheLayer<any>;
  private sessionCache: CacheLayer<any>;
  private globalCache: CacheLayer<any>;
  private translationCache: CacheLayer<any>;

  constructor() {
    // Request layer: small, short-lived (5 minutes)
    this.requestCache = new CacheLayer({
      maxSize: 100,
      defaultTtl: 5 * 60 * 1000, // 5 minutes
    });

    // Session layer: medium, moderate TTL (1 hour)
    this.sessionCache = new CacheLayer({
      maxSize: 500,
      defaultTtl: 60 * 60 * 1000, // 1 hour
    });

    // Global layer: large, long-lived (1 week)
    this.globalCache = new CacheLayer({
      maxSize: 5000,
      defaultTtl: 7 * 24 * 60 * 60 * 1000, // 1 week
    });

    // Translation layer: dedicated for translation results (1 week)
    this.translationCache = new CacheLayer({
      maxSize: 2000,
      defaultTtl: 7 * 24 * 60 * 60 * 1000, // 1 week
    });
  }

  /**
   * Get value from specified layer
   * Layer priority: request → session → global
   */
  get<T>(key: string, layer: 'request' | 'session' | 'global' | 'translation' = 'global'): T | undefined {
    const cacheLayer = this.getCacheLayer(layer);
    return cacheLayer.get(key) as T | undefined;
  }

  /**
   * Set value in specified layer
   */
  set<T>(key: string, value: T, layer: 'request' | 'session' | 'global' | 'translation' = 'global', ttl?: number): void {
    const cacheLayer = this.getCacheLayer(layer);
    cacheLayer.set(key, value, ttl);
  }

  /**
   * Delete from all layers
   */
  delete(key: string): void {
    this.requestCache.delete(key);
    this.sessionCache.delete(key);
    this.globalCache.delete(key);
    this.translationCache.delete(key);
  }

  /**
   * Clear specific layer or all layers
   */
  clear(layer?: 'request' | 'session' | 'global' | 'translation'): void {
    if (layer) {
      const cacheLayer = this.getCacheLayer(layer);
      cacheLayer.clear();
    } else {
      // Clear all layers
      this.requestCache.clear();
      this.sessionCache.clear();
      this.globalCache.clear();
      this.translationCache.clear();
    }
  }

  /**
   * Get cache key for concept generation result
   * Format: concept:{depth}:{language}:{hash}
   */
  getConceptKey(concept: string, depth: 'intro' | 'intermediate' | 'advanced', language: 'en' | 'ja'): string {
    const normalized = concept.toLowerCase().trim();
    return `concept:${depth}:${language}:${this.hash(normalized)}`;
  }

  /**
   * Get cache key for translation result
   * Format: translation:{text}:{source_lang}:{target_lang}:{hash}
   */
  getTranslationKey(text: string, sourceLanguage: string, targetLanguage: string): string {
    const normalized = text.toLowerCase().trim();
    return `translation:${sourceLanguage}:${targetLanguage}:${this.hash(normalized)}`;
  }

  /**
   * Get statistics for all cache layers
   */
  getStats(): Record<string, any> {
    return {
      request: this.requestCache.getStats(),
      session: this.sessionCache.getStats(),
      global: this.globalCache.getStats(),
      translation: this.translationCache.getStats(),
    };
  }

  /**
   * Get total cache size across all layers
   */
  getTotalSize(): number {
    const stats = this.getStats();
    return stats.request.size + stats.session.size + stats.global.size + stats.translation.size;
  }

  /**
   * Simple hash function for cache keys
   * Uses first 50 chars to keep keys manageable
   */
  private hash(value: string): string {
    let hash = 0;
    const str = value.substring(0, 50);

    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      // eslint-disable-next-line no-bitwise
      hash = (hash << 5) - hash + char;
      // eslint-disable-next-line no-bitwise
      hash = hash & hash; // Convert to 32bit integer
    }

    return Math.abs(hash).toString(16);
  }

  /**
   * Get cache layer by name
   */
  private getCacheLayer(layer: 'request' | 'session' | 'global' | 'translation'): CacheLayer<any> {
    switch (layer) {
      case 'request':
        return this.requestCache;
      case 'session':
        return this.sessionCache;
      case 'translation':
        return this.translationCache;
      case 'global':
      default:
        return this.globalCache;
    }
  }
}

// Export singleton instance for application-wide use
export const cacheManager = new CacheManager();
