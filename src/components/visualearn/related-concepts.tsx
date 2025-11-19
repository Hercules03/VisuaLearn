'use client';

import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Lightbulb } from 'lucide-react';

type RelatedConceptsProps = {
  concepts: string[];
  onConceptClick: (concept: string) => void;
  isLoading: boolean;
};

export function RelatedConcepts({
  concepts,
  onConceptClick,
  isLoading,
}: RelatedConceptsProps) {
  if (!concepts || concepts.length === 0) {
    return null;
  }

  return (
    <Card className="animate-in fade-in">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 font-headline">
          <Lightbulb className="h-5 w-5 text-primary" />
          Explore Related Concepts
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2">
          {concepts.map((concept) => (
            <Button
              key={concept}
              variant="outline"
              size="sm"
              onClick={() => onConceptClick(concept)}
              disabled={isLoading}
            >
              {concept}
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
