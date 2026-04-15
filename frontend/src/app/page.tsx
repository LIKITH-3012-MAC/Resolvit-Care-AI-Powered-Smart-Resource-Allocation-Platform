import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { TrustStrip } from "@/components/landing/TrustStrip";
import { Features } from "@/components/landing/Features";
import { Footer } from "@/components/landing/Footer"; // I'll create this next

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <Navbar />
      <Hero />
      <TrustStrip />
      <Features />
      
      {/* 
        Remaining sections like DashboardPreview, Impact, CTA 
        will be added as separate components 
      */}
      
      <Footer />
    </main>
  );
}
