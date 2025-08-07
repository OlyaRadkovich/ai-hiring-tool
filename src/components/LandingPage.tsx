import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, FileText, VideoIcon, BarChart3, Shield, Zap } from "lucide-react";

interface LandingPageProps {
  onGetStarted: () => void;
}

export default function LandingPage({ onGetStarted }: LandingPageProps) {
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
          <Button onClick={onGetStarted} className="bg-gradient-primary hover:shadow-glow transition-all duration-300">
            Get Started
          </Button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-24 px-4">
        <div className="container mx-auto text-center">
          <Badge variant="secondary" className="mb-6 px-4 py-2">
            🚀 AI-Powered Interview Analysis
          </Badge>
          <h2 className="text-5xl font-bold mb-6 bg-gradient-primary bg-clip-text text-transparent">
            Transform Your Hiring Process
          </h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
            Leverage advanced AI to prepare, analyze, and evaluate candidate interviews with unprecedented accuracy.
            Generate comprehensive reports and make data-driven hiring decisions.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Button 
              size="lg" 
              onClick={onGetStarted}
              className="bg-gradient-primary hover:shadow-glow transition-all duration-300 px-8"
            >
              Start Free Trial
            </Button>
            <Button variant="outline" size="lg" className="border-primary/20 hover:border-primary/40">
              Watch Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold mb-4">Powerful Features for Modern Recruitment</h3>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Everything you need to streamline your interview process and make better hiring decisions
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="shadow-card hover:shadow-elegant transition-all duration-300 bg-gradient-card border-0">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <FileText className="w-6 h-6 text-primary" />
                </div>
                <CardTitle className="text-xl">Smart Preparation</CardTitle>
                <CardDescription>
                  Upload CVs and get AI-generated interview questions tailored to each candidate's background
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="shadow-card hover:shadow-elegant transition-all duration-300 bg-gradient-card border-0">
              <CardHeader>
                <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                  <VideoIcon className="w-6 h-6 text-accent" />
                </div>
                <CardTitle className="text-xl">Video Analysis</CardTitle>
                <CardDescription>
                  Automatically transcribe and analyze video interviews using advanced speech-to-text technology
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="shadow-card hover:shadow-elegant transition-all duration-300 bg-gradient-card border-0">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <BarChart3 className="w-6 h-6 text-primary" />
                </div>
                <CardTitle className="text-xl">Competency Scoring</CardTitle>
                <CardDescription>
                  Evaluate candidates against your custom competency matrix with detailed scoring and feedback
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="shadow-card hover:shadow-elegant transition-all duration-300 bg-gradient-card border-0">
              <CardHeader>
                <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                  <Brain className="w-6 h-6 text-accent" />
                </div>
                <CardTitle className="text-xl">AI Insights</CardTitle>
                <CardDescription>
                  Get intelligent recommendations and cultural fit assessments powered by advanced AI models
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="shadow-card hover:shadow-elegant transition-all duration-300 bg-gradient-card border-0">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="w-6 h-6 text-primary" />
                </div>
                <CardTitle className="text-xl">Secure & Compliant</CardTitle>
                <CardDescription>
                  Enterprise-grade security with GDPR compliance and secure data handling for sensitive information
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="shadow-card hover:shadow-elegant transition-all duration-300 bg-gradient-card border-0">
              <CardHeader>
                <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                  <Zap className="w-6 h-6 text-accent" />
                </div>
                <CardTitle className="text-xl">Fast Processing</CardTitle>
                <CardDescription>
                  Process interviews up to 1 hour in under 3 minutes with comprehensive DOCX report generation
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-primary text-primary-foreground">
        <div className="container mx-auto text-center">
          <h3 className="text-3xl font-bold mb-4">Ready to Transform Your Hiring?</h3>
          <p className="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
            Join forward-thinking companies already using AI to make better hiring decisions
          </p>
          <Button 
            size="lg" 
            variant="secondary"
            onClick={onGetStarted}
            className="px-8 hover:shadow-lg transition-all duration-300"
          >
            Start Your Free Trial
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 border-t bg-card">
        <div className="container mx-auto text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-lg font-semibold">InterviewAI</span>
          </div>
          <p className="text-muted-foreground">
            © 2024 InterviewAI. Transforming recruitment with artificial intelligence.
          </p>
        </div>
      </footer>
    </div>
  );
}