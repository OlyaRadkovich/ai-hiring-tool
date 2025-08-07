import { useState } from "react";
import LandingPage from "@/components/LandingPage";
import AuthPage from "@/components/AuthPage";
import Dashboard from "@/components/Dashboard";

const Index = () => {
  const [currentView, setCurrentView] = useState<"landing" | "auth" | "dashboard">("landing");

  const handleGetStarted = () => {
    setCurrentView("auth");
  };

  const handleAuthenticated = () => {
    setCurrentView("dashboard");
  };

  const handleLogout = () => {
    setCurrentView("landing");
  };

  if (currentView === "auth") {
    return <AuthPage onAuthenticated={handleAuthenticated} />;
  }

  if (currentView === "dashboard") {
    return <Dashboard onLogout={handleLogout} />;
  }

  return <LandingPage onGetStarted={handleGetStarted} />;
};

export default Index;
