import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  Video, 
  Upload, 
  Brain, 
  Download, 
  Play, 
  FileText,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Users,
  Target
} from "lucide-react";

export default function InterviewResults() {
  const [videoLink, setVideoLink] = useState("");
  const [competencyMatrix, setCompetencyMatrix] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<any>(null);

  const handleMatrixUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setCompetencyMatrix(file);
    }
  };

  const handleAnalyzeInterview = async () => {
    setIsProcessing(true);
    
    // Simulate AI processing
    setTimeout(() => {
      setAnalysisResults({
        transcription: "The candidate demonstrated strong technical knowledge when discussing React hooks and state management. They provided specific examples of performance optimization techniques including code splitting and lazy loading. When asked about team leadership, they shared their experience mentoring 3 junior developers and implementing code review processes. The candidate showed enthusiasm for learning new technologies and expressed interest in contributing to architectural decisions.",
        scores: {
          technical: 85,
          communication: 78,
          leadership: 82,
          cultural: 75,
          overall: 80
        },
        strengths: [
          "Strong technical expertise in React and TypeScript",
          "Clear communication style with concrete examples",
          "Proven leadership experience with junior developers",
          "Proactive approach to code quality and best practices"
        ],
        concerns: [
          "Limited experience with large-scale system architecture",
          "Could benefit from more exposure to cross-functional collaboration",
          "Might need support transitioning to senior leadership role"
        ],
        recommendation: "RECOMMEND HIRE",
        reasoning: "Candidate demonstrates strong technical skills and leadership potential. While there are areas for growth, their foundation is solid and they show clear enthusiasm for learning. Recommend proceeding to final round with focus on architecture discussions.",
        topicsDiscussed: [
          "React Hooks & State Management",
          "Performance Optimization",
          "Code Review Processes",
          "Team Mentoring",
          "Testing Strategies",
          "CI/CD Implementation"
        ]
      });
      setIsProcessing(false);
    }, 3000);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return "bg-green-100";
    if (score >= 60) return "bg-yellow-100";
    return "bg-red-100";
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Video className="w-5 h-5 text-primary" />
              <span>Interview Video</span>
            </CardTitle>
            <CardDescription>
              Provide a Google Drive link to the recorded interview
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="video-link">Google Drive Video Link</Label>
              <Input
                id="video-link"
                type="url"
                placeholder="https://drive.google.com/file/d/..."
                value={videoLink}
                onChange={(e) => setVideoLink(e.target.value)}
              />
            </div>
            {videoLink && (
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Play className="w-4 h-4" />
                <span>Video link ready for processing</span>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Upload className="w-5 h-5 text-accent" />
              <span>Competency Matrix</span>
            </CardTitle>
            <CardDescription>
              Upload your evaluation criteria and scoring framework
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
              <input
                type="file"
                id="matrix-upload"
                accept=".pdf,.docx"
                onChange={handleMatrixUpload}
                className="hidden"
              />
              <label htmlFor="matrix-upload" className="cursor-pointer">
                <FileText className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
                <p className="text-sm text-muted-foreground mb-2">
                  {competencyMatrix ? competencyMatrix.name : "Click to upload matrix"}
                </p>
                <p className="text-xs text-muted-foreground">
                  PDF or DOCX format
                </p>
              </label>
            </div>
            {competencyMatrix && (
              <Badge variant="secondary" className="mt-3">
                ✓ {competencyMatrix.name} uploaded
              </Badge>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Process Button */}
      <div className="text-center">
        <Button
          onClick={handleAnalyzeInterview}
          disabled={!videoLink || !competencyMatrix || isProcessing}
          className="bg-gradient-primary hover:shadow-glow transition-all duration-300 px-8"
          size="lg"
        >
          {isProcessing ? (
            <>
              <Brain className="w-5 h-5 mr-2 animate-spin" />
              Processing Interview... (AI transcription & analysis)
            </>
          ) : (
            <>
              <Brain className="w-5 h-5 mr-2" />
              Analyze Interview with AI
            </>
          )}
        </Button>
      </div>

      {/* Processing Status */}
      {isProcessing && (
        <Card className="shadow-card">
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between text-sm">
                <span>Downloading video from Google Drive...</span>
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
              <div className="flex items-center justify-between text-sm">
                <span>Transcribing audio with AI...</span>
                <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              </div>
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span>Analyzing content against competency matrix...</span>
                <div className="w-5 h-5" />
              </div>
              <Progress value={60} className="w-full" />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analysis Results */}
      {analysisResults && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-2xl font-bold">Interview Analysis Results</h3>
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export DOCX Report
            </Button>
          </div>

          {/* Overall Recommendation */}
          <Card className="shadow-card border-l-4 border-l-green-500">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="w-5 h-5 text-green-600" />
                <span>Final Recommendation</span>
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  {analysisResults.recommendation}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground leading-relaxed">
                {analysisResults.reasoning}
              </p>
            </CardContent>
          </Card>

          {/* Competency Scores */}
          <Card className="shadow-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-primary" />
                <span>Competency Assessment</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                {Object.entries(analysisResults.scores).map(([category, score]: [string, number]) => (
                  <div key={category} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium capitalize">{category}</span>
                      <span className={`font-bold ${getScoreColor(score)}`}>
                        {score}%
                      </span>
                    </div>
                    <Progress value={score} className="h-2" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Strengths & Concerns */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-green-600">
                  <CheckCircle className="w-5 h-5" />
                  <span>Key Strengths</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {analysisResults.strengths.map((strength: string, index: number) => (
                    <li key={index} className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-sm">{strength}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-yellow-600">
                  <AlertCircle className="w-5 h-5" />
                  <span>Areas of Concern</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {analysisResults.concerns.map((concern: string, index: number) => (
                    <li key={index} className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-sm">{concern}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Topics Discussed */}
          <Card className="shadow-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="w-5 h-5 text-accent" />
                <span>Topics Discussed</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {analysisResults.topicsDiscussed.map((topic: string, index: number) => (
                  <Badge key={index} variant="outline" className="px-3 py-1">
                    {topic}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Transcript Preview */}
          <Card className="shadow-card">
            <CardHeader>
              <CardTitle>Interview Transcript</CardTitle>
              <CardDescription>
                AI-generated transcript from the video interview
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-muted/50 rounded-lg p-4 max-h-60 overflow-y-auto">
                <p className="text-sm leading-relaxed">{analysisResults.transcription}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}