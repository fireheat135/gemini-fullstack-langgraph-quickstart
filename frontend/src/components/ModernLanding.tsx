import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Search, 
  BarChart3, 
  Brain, 
  Zap, 
  Sparkles, 
  ArrowRight, 
  Globe,
  Target,
  TrendingUp,
  FileText,
  Users,
  Shield,
  Rocket
} from 'lucide-react';

interface ModernLandingProps {
  onGetStarted: () => void;
}

export function ModernLanding({ onGetStarted }: ModernLandingProps) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Research',
      description: 'Advanced LangGraph workflows with multi-provider AI integration',
      stats: '10x faster'
    },
    {
      icon: BarChart3,
      title: 'Advanced Analytics',
      description: 'Real-time performance tracking with predictive insights',
      stats: '360° view'
    },
    {
      icon: Search,
      title: 'Smart SEO Research',
      description: 'Comprehensive keyword analysis and competitor intelligence',
      stats: '50+ metrics'
    },
    {
      icon: FileText,
      title: 'Content Generation',
      description: 'AI-driven content creation with fact-checking and optimization',
      stats: '99% accuracy'
    },
    {
      icon: Target,
      title: 'Precision Targeting',
      description: 'Audience analysis and content personalization at scale',
      stats: '3x engagement'
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'End-to-end encryption with role-based access control',
      stats: 'SOC2 compliant'
    }
  ];

  const metrics = [
    { value: '10M+', label: 'Keywords Analyzed' },
    { value: '50K+', label: 'Content Pieces' },
    { value: '99.9%', label: 'Uptime' },
    { value: '24/7', label: 'AI Support' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white overflow-hidden relative">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden">
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            background: `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(139, 92, 246, 0.15), transparent 40%)`
          }}
        />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:14px_14px] opacity-20" />
      </div>

      {/* Hero Section */}
      <section className="relative z-10 pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className={`text-center transform transition-all duration-1000 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
            <div className="flex items-center justify-center mb-6">
              <Badge variant="outline" className="border-purple-400/50 text-purple-300 bg-purple-500/10 px-4 py-2">
                <Sparkles className="w-4 h-4 mr-2" />
                Next-Gen SEO Platform
              </Badge>
            </div>
            
            <h1 className="text-6xl md:text-8xl font-bold mb-6 bg-gradient-to-r from-white via-purple-200 to-purple-400 bg-clip-text text-transparent leading-tight">
              Scrib AI
            </h1>
            
            <p className="text-xl md:text-2xl text-slate-300 mb-8 max-w-3xl mx-auto leading-relaxed">
              Revolutionary SEO content creation with advanced AI analytics, 
              <span className="text-purple-400 font-semibold"> real-time insights</span>, and 
              <span className="text-blue-400 font-semibold"> predictive intelligence</span>
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <Button 
                size="lg" 
                onClick={onGetStarted}
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-8 py-4 text-lg font-semibold group transition-all duration-300 transform hover:scale-105"
              >
                Start Creating
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="border-purple-400/50 text-purple-300 hover:bg-purple-500/10 px-8 py-4 text-lg"
              >
                View Demo
              </Button>
            </div>
          </div>

          {/* Metrics */}
          <div className={`grid grid-cols-2 md:grid-cols-4 gap-8 mb-20 transform transition-all duration-1000 delay-300 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
            {metrics.map((metric, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-purple-400 mb-2">{metric.value}</div>
                <div className="text-slate-400 text-sm">{metric.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className={`text-center mb-16 transform transition-all duration-1000 delay-500 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
              Powerful Features
            </h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Enterprise-grade SEO tools powered by cutting-edge AI technology
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card 
                key={index} 
                className={`bg-slate-800/50 border-slate-700/50 backdrop-blur-sm hover:bg-slate-800/70 transition-all duration-500 group transform ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}
                style={{ transitionDelay: `${600 + index * 100}ms` }}
              >
                <CardHeader>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                      <feature.icon className="w-6 h-6 text-white" />
                    </div>
                    <Badge variant="secondary" className="bg-purple-500/20 text-purple-300 border-purple-400/30">
                      {feature.stats}
                    </Badge>
                  </div>
                  <CardTitle className="text-white text-xl group-hover:text-purple-300 transition-colors">
                    {feature.title}
                  </CardTitle>
                  <CardDescription className="text-slate-400 leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <Card className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 border-purple-500/30 backdrop-blur-sm">
            <CardContent className="p-12">
              <Rocket className="w-16 h-16 text-purple-400 mx-auto mb-6" />
              <h3 className="text-3xl md:text-4xl font-bold text-white mb-6">
                Ready to Transform Your SEO Strategy?
              </h3>
              <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
                Join thousands of content creators and marketers who trust Scrib AI 
                for their SEO content needs.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Input 
                  placeholder="Enter your email address" 
                  className="bg-slate-800/50 border-slate-600 text-white placeholder:text-slate-400 max-w-sm"
                />
                <Button 
                  size="lg" 
                  onClick={onGetStarted}
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-8 font-semibold group"
                >
                  Get Started Free
                  <Zap className="ml-2 w-5 h-5 group-hover:scale-110 transition-transform" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-700/50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <h4 className="text-2xl font-bold text-white mb-4">Scrib AI</h4>
              <p className="text-slate-400 mb-6 max-w-md">
                The most advanced SEO content platform powered by cutting-edge AI technology.
              </p>
              <div className="flex space-x-4">
                {[Globe, TrendingUp, Users].map((Icon, index) => (
                  <div key={index} className="w-10 h-10 bg-slate-800 rounded-lg flex items-center justify-center hover:bg-purple-600 transition-colors cursor-pointer">
                    <Icon className="w-5 h-5 text-slate-400 hover:text-white" />
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h5 className="text-white font-semibold mb-4">Platform</h5>
              <div className="space-y-2 text-slate-400">
                <div className="hover:text-purple-400 cursor-pointer transition-colors">Analytics</div>
                <div className="hover:text-purple-400 cursor-pointer transition-colors">Research</div>
                <div className="hover:text-purple-400 cursor-pointer transition-colors">Content</div>
                <div className="hover:text-purple-400 cursor-pointer transition-colors">API</div>
              </div>
            </div>
            <div>
              <h5 className="text-white font-semibold mb-4">Support</h5>
              <div className="space-y-2 text-slate-400">
                <div className="hover:text-purple-400 cursor-pointer transition-colors">Documentation</div>
                <div className="hover:text-purple-400 cursor-pointer transition-colors">Community</div>
                <div className="hover:text-purple-400 cursor-pointer transition-colors">Help Center</div>
                <div className="hover:text-purple-400 cursor-pointer transition-colors">Contact</div>
              </div>
            </div>
          </div>
          <div className="border-t border-slate-700/50 mt-12 pt-8 text-center text-slate-400">
            <p>&copy; 2025 Scrib AI. All rights reserved. Built with ❤️ and cutting-edge AI.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}