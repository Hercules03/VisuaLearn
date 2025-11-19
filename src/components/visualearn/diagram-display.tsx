'use client';

import React, { useEffect, useRef } from 'react';
import Image from 'next/image';
import { Card, CardContent } from '@/components/ui/card';
import { PlaceHolderImages } from '@/lib/placeholder-images';

interface DiagramDisplayProps {
  svgContent: string | null;
  isLoading: boolean;
  currentStep: number;
}

export function DiagramDisplay({
  svgContent,
  isLoading,
  currentStep,
}: DiagramDisplayProps) {
  const svgContainerRef = useRef<HTMLDivElement>(null);
  const placeholder = PlaceHolderImages.find(
    (p) => p.id === 'visualearn-placeholder'
  );

  useEffect(() => {
    const container = svgContainerRef.current;
    if (!container) return;

    if (svgContent && container.innerHTML !== svgContent) {
      container.innerHTML = svgContent;
      const svg = container.querySelector('svg');
      if (svg) {
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '100%');
        svg.style.maxWidth = '100%';
        svg.style.height = 'auto';
      }
    } else if (!svgContent && !isLoading) {
      container.innerHTML = '';
    }

    if (svgContent) {
      container.querySelectorAll('.highlighted').forEach((el) => {
        el.classList.remove('highlighted');
      });

      if (currentStep >= 0) {
        const elementToHighlight = container.querySelector(
          `#step-${currentStep}`
        );
        if (elementToHighlight) {
          elementToHighlight.classList.add('highlighted');
        }
      }
    }
  }, [svgContent, currentStep, isLoading]);

  return (
    <Card className="flex-1 w-full h-full flex items-center justify-center overflow-hidden min-h-[400px] md:min-h-[600px] lg:min-h-0">
      <CardContent className="w-full h-full p-4 md:p-6 flex items-center justify-center">
        {isLoading ? (
          <div className="w-full h-full flex items-center justify-center">
             <svg className="animate-spin h-12 w-12 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        ) : svgContent ? (
          <div ref={svgContainerRef} className="w-full h-full" />
        ) : (
          <div className="text-center text-muted-foreground flex flex-col items-center gap-4 animate-in fade-in">
            {placeholder && (
              <Image
                src={placeholder.imageUrl}
                alt={placeholder.description}
                width={400}
                height={300}
                className="rounded-lg object-cover shadow-md"
                data-ai-hint={placeholder.imageHint}
                priority
              />
            )}
            <h3 className="text-lg font-semibold font-headline text-foreground">
              Welcome to VisuaLearn
            </h3>
            <p className="max-w-md">
              Enter a concept you want to learn about, and we'll generate an
              interactive diagram to explain it.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
