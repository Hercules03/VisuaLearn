'use client';

import * as z from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { ArrowLeft, ArrowRight, Loader2 } from 'lucide-react';
import type { GenerateInteractiveDiagramOutput } from '@/ai/flows/generate-interactive-diagram';

const formSchema = z.object({
  concept: z
    .string()
    .min(3, 'Please enter a concept with at least 3 characters.'),
});

type ControlPanelProps = {
  onSubmit: (values: z.infer<typeof formSchema>) => void;
  isLoading: boolean;
  diagramData: GenerateInteractiveDiagramOutput['diagramData'] | null;
  currentStep: number;
  setCurrentStep: React.Dispatch<React.SetStateAction<number>>;
  isSimulating: boolean;
  setIsSimulating: React.Dispatch<React.SetStateAction<boolean>>;
};

export function ControlPanel({
  onSubmit,
  isLoading,
  diagramData,
  currentStep,
  setCurrentStep,
  isSimulating,
  setIsSimulating,
}: ControlPanelProps) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { concept: '' },
  });

  const handleNext = () => {
    if (diagramData && currentStep < diagramData.steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <Card className="w-full flex flex-col">
      <CardHeader>
        <CardTitle className="font-headline">Control Panel</CardTitle>
        <CardDescription>
          Enter a concept and explore the visualization.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-grow flex flex-col gap-6">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="concept"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Concept to Learn</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="e.g., Load Balancer, Photosynthesis"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" disabled={isLoading} className="w-full">
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Generate Diagram
            </Button>
          </form>
        </Form>

        {diagramData && (
          <div className="space-y-6 animate-in fade-in">
            <div className="space-y-4">
              <h3 className="font-semibold font-headline text-lg">Tutorial</h3>
              <div className="p-4 bg-muted/50 rounded-lg space-y-4 text-sm min-h-[120px]">
                <div>
                  <h4 className="font-semibold mb-1">Explanation</h4>
                  <p className="text-muted-foreground">
                    {diagramData.explanation}
                  </p>
                </div>
                {diagramData.steps[currentStep] && (
                  <div>
                    <h4 className="font-semibold mb-1">Step {currentStep + 1}</h4>
                    <p className="text-muted-foreground">
                      {diagramData.steps[currentStep]}
                    </p>
                  </div>
                )}
              </div>
              <div className="flex items-center justify-between">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handlePrev}
                  disabled={currentStep <= 0 || isSimulating}
                >
                  <ArrowLeft className="h-4 w-4" />
                  <span className="sr-only">Previous Step</span>
                </Button>
                <span className="text-sm font-medium text-muted-foreground">
                  Step {currentStep + 1} / {diagramData.steps.length}
                </span>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handleNext}
                  disabled={
                    currentStep >= diagramData.steps.length - 1 || isSimulating
                  }
                >
                  <ArrowRight className="h-4 w-4" />
                  <span className="sr-only">Next Step</span>
                </Button>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-semibold font-headline text-lg">
                Simulation
              </h3>
              <div className="flex items-center space-x-2">
                <Switch
                  id="simulation-mode"
                  checked={isSimulating}
                  onCheckedChange={setIsSimulating}
                />
                <Label htmlFor="simulation-mode">Start/Stop Simulation</Label>
              </div>
              <p className="text-xs text-muted-foreground">
                Toggle to loop through all the steps automatically.
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
