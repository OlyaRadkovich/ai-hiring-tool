import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Brain, FileText, Video } from "lucide-react";
import InterviewPreparation from "./InterviewPreparation";
import InterviewResults from "./InterviewResults";
import { toast } from "./ui/use-toast";

interface DashboardProps {
  onLogout: () => void;
}

interface MatchingItem {
  criterion: string;
  match: string;
  comment: string;
}

interface Conclusion {
  summary: string;
  recommendations: string;
  interview_topics: string[];
  values_assessment: string;
}

interface Report {
  first_name: string | null;
  last_name: string | null;
  matching_table: MatchingItem[];
  candidate_profile: string;
  conclusion: Conclusion;
}

interface PreparationAnalysisResponse {
  message: string;
  success: boolean;
  report: Report;
}

interface CandidateInfo {
  full_name: string;
  experience_years: string;
  tech_stack: string[];
  projects: string[];
  domains: string[];
  tasks: string[];
}

interface InterviewAnalysis {
  topics: string[];
  tech_assignment: string;
  knowledge_assessment: string;
}

interface CommunicationSkills {
  assessment: string;
}

interface ForeignLanguages {
  assessment: string;
}

interface FinalConclusion {
  recommendation: string;
  assessed_level: string;
  summary: string;
}

interface FullReport {
  ai_summary: string;
  candidate_info: CandidateInfo;
  interview_analysis: InterviewAnalysis;
  communication_skills: CommunicationSkills;
  foreign_languages: ForeignLanguages;
  team_fit: string;
  additional_information: string[];
  conclusion: FinalConclusion;
  recommendations_for_candidate: string[];
}

interface ResultsAnalysisResponse {
  message: string;
  success: boolean;
  report: FullReport;
}

interface CacheData {
  preparation?: PreparationAnalysisResponse;
  results?: ResultsAnalysisResponse;
}

interface LoadingStatus {
  preparation: boolean;
  results: boolean;
}

export default function Dashboard({ onLogout }: DashboardProps) {
  const [activeTab, setActiveTab] = useState("preparation");
  const [cache, setCache] = useState<CacheData>({});
  const [loadingStatus, setLoadingStatus] = useState<LoadingStatus>({
    preparation: false,
    results: false,
  });

  const updateCache = (tab: "preparation" | "results", data: any) => {
    setCache((prevCache) => ({
      ...prevCache,
      [tab]: data,
    }));
  };

  const setLoading = (tab: "preparation" | "results", status: boolean) => {
    setLoadingStatus((prevStatus) => ({
      ...prevStatus,
      [tab]: status,
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <header className="border-b bg-card/95 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6 text-primary-foreground" />
            </div>
            <h1 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              InterviewAI
            </h1>
          </div>

          <Button variant="ghost" size="sm" onClick={onLogout}>
            Back to Home
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">
            Interview Analysis Platform
          </h2>
          <p className="text-muted-foreground">
            Prepare for interviews and analyze candidate performance with
            AI-powered insights
          </p>
        </div>
        <Card className="shadow-elegant bg-gradient-card border-0">
          <Tabs
            value={activeTab}
            onValueChange={setActiveTab}
            className="w-full"
          >
            <CardHeader>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger
                  value="preparation"
                  className="flex items-center space-x-2"
                >
                  <FileText className="w-4 h-4" />
                  <span>Interview Preparation</span>
                </TabsTrigger>
                <TabsTrigger
                  value="results"
                  className="flex items-center space-x-2"
                >
                  <Video className="w-4 h-4" />
                  <span>Interview Results</span>
                </TabsTrigger>
              </TabsList>
            </CardHeader>
            <CardContent>
              <TabsContent value="preparation" className="mt-0">
                <InterviewPreparation
                  cachedData={cache.preparation}
                  updateCache={(data) => updateCache("preparation", data)}
                  isLoading={loadingStatus.preparation}
                  setIsLoading={(status) => setLoading("preparation", status)}
                />
              </TabsContent>

              <TabsContent value="results" className="mt-0">
                <InterviewResults
                  cachedData={cache.results}
                  updateCache={(data) => updateCache("results", data)}
                  isProcessing={loadingStatus.results}
                  setIsProcessing={(status) => setLoading("results", status)}
                />
              </TabsContent>
            </CardContent>
          </Tabs>
        </Card>
      </main>
    </div>
  );
}