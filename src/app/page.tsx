'use client';

import { useState, useEffect } from 'react';
import { useToast } from '@/hooks/use-toast';
import { handleGeneration } from '@/lib/actions';
import { Header } from '@/components/visualearn/header';
import { ControlPanel } from '@/components/visualearn/control-panel';
import { DiagramDisplay } from '@/components/visualearn/diagram-display';
import { RelatedConcepts } from '@/components/visualearn/related-concepts';
import type { GenerateInteractiveDiagramOutput } from '@/ai/flows/generate-interactive-diagram';

type GenerationResult = {
  diagramData: GenerateInteractiveDiagramOutput['diagramData'];
  relatedConcepts: string[];
};

export default function Home() {
  const [generationResult, setGenerationResult] =
    useState<GenerationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [isSimulating, setIsSimulating] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (isSimulating && generationResult?.diagramData.steps.length) {
      const interval = setInterval(() => {
        setCurrentStep(
          (prev) => (prev + 1) % generationResult.diagramData.steps.length
        );
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [isSimulating, generationResult]);

  const onFormSubmit = async (values: { concept: string }) => {
    setIsLoading(true);
    setGenerationResult(null);
    setCurrentStep(-1);
    setIsSimulating(false);

    const result = await handleGeneration(values.concept);
    setIsLoading(false);

    if (result.error) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: result.error,
      });
    } else if (result.diagramData && result.relatedConcepts) {
      setGenerationResult({
        diagramData: result.diagramData,
        relatedConcepts: result.relatedConcepts,
      });
      setCurrentStep(0);
    }
  };

  const handleConceptClick = (concept: string) => {
    onFormSubmit({ concept });
  };

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Header />
      <main className="flex-grow container mx-auto p-4 sm:p-6 lg:p-8">
        <div className="flex flex-col lg:flex-row gap-6 lg:gap-8 items-start">
          <div className="w-full lg:w-auto lg:max-w-md flex flex-col gap-6">
            <ControlPanel
              onSubmit={onFormSubmit}
              isLoading={isLoading}
              diagramData={generationResult?.diagramData ?? null}
              currentStep={currentStep}
              setCurrentStep={setCurrentStep}
              isSimulating={isSimulating}
              setIsSimulating={setIsSimulating}
            />
            <RelatedConcepts
              concepts={generationResult?.relatedConcepts ?? []}
              onConceptClick={handleConceptClick}
              isLoading={isLoading}
            />
          </div>
          <DiagramDisplay
            svgContent={generationResult?.diagramData.svgContent ?? null}
            isLoading={isLoading}
            currentStep={currentStep}
          />
        </div>
      </main>
    </div>
  );
}
