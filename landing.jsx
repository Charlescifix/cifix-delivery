import React from "react";
import { motion } from "framer-motion";
import { Sparkles, Rocket, ShieldCheck, GraduationCap, ArrowRight, Star, BookOpen, Users } from "lucide-react";

// Floating animation helper
export const floating = (delay = 0, duration = 12, y = 18) => ({
  initial: { y: 0 },
  animate: { y: [0, -y, 0] },
  transition: { repeat: Infinity, duration, ease: "easeInOut", delay },
});

// Simple fade-in variant
export const fadeIn = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, ease: "easeOut" },
};

export default function CifixLanding() {
  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-white text-gray-800">
      {/* Soft background field (safe gradient + noise) */}
      <div
        className="pointer-events-none absolute inset-0 -z-20"
        aria-hidden="true"
        style={{
          backgroundImage:
            "radial-gradient(1200px 600px at 10% -10%, rgba(59,130,246,0.12), transparent)," +
            "radial-gradient(1000px 500px at 110% 110%, rgba(16,185,129,0.10), transparent)," +
            "radial-gradient(800px 400px at 85% 35%, rgba(250,204,21,0.10), transparent)",
          backgroundRepeat: "no-repeat",
        }}
      />
      {/* Ultra‑subtle noise overlay */}
      <div
        className="pointer-events-none absolute inset-0 -z-10 opacity-[0.06]"
        aria-hidden="true"
        style={{
          backgroundImage:
            "repeating-linear-gradient(0deg, rgba(0,0,0,0.03) 0px, rgba(0,0,0,0.03) 1px, transparent 1px, transparent 2px)",
          mixBlendMode: "multiply",
        }}
      />

      {/* Decorative floating glyphs */}
      <motion.div className="pointer-events-none absolute left-6 top-10 hidden md:block" {...floating(0.4, 14, 14)} aria-hidden="true">
        <IconChip label="C I F I X" />
      </motion.div>
      <motion.div className="pointer-events-none absolute right-8 top-24 hidden lg:block" {...floating(0.8, 16, 16)} aria-hidden="true">
        <IconBadge icon={<ShieldCheck className="h-5 w-5" />} text="Safe Learning" />
      </motion.div>
      <motion.div className="pointer-events-none absolute bottom-20 left-10 hidden lg:block" {...floating(1.2, 15, 12)} aria-hidden="true">
        <IconBadge icon={<GraduationCap className="h-5 w-5" />} text="Kids Hub" />
      </motion.div>

      {/* Header */}
      <header className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gray-900 text-white shadow-sm">
            <Sparkles className="h-5 w-5" />
          </div>
          <div className="leading-tight">
            <div className="text-base font-semibold tracking-tight">CIFIX Kids Hub</div>
            <div className="text-xs text-gray-500">Learning Made Fun</div>
          </div>
        </div>
        <nav className="hidden items-center gap-6 md:flex">
          <a href="#about" className="text-sm text-gray-600 hover:text-gray-900">About</a>
          <a href="#modules" className="text-sm text-gray-600 hover:text-gray-900">Features</a>
          <a href="#safety" className="text-sm text-gray-600 hover:text-gray-900">Safety</a>
        </nav>
        <div className="flex items-center gap-3">
          <a
            href="/parent"
            className="hidden rounded-xl border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 md:block"
          >Parent Portal</a>
          <a
            href="/login"
            className="rounded-xl bg-gray-900 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-gray-800"
          >Student Login</a>
        </div>
      </header>

      {/* Hero */}
      <main className="relative mx-auto flex w-full max-w-7xl flex-col items-center px-6 pt-10 pb-16 md:pt-16 md:pb-24">
        <motion.div className="mx-auto max-w-3xl text-center" {...fadeIn}>
          <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white px-3 py-1 text-xs font-medium text-gray-600 shadow-sm">
            Powered by <span className="font-semibold text-gray-900">AI Learning Technology</span>
          </div>
          <h1 className="mt-5 text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl">
            Welcome to <span className="bg-gradient-to-r from-blue-600 to-emerald-500 bg-clip-text text-transparent">CIFIX Kids Hub</span>
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-base leading-7 text-gray-600 sm:text-lg">
            A safe, fun learning platform where kids explore, discover, and grow. Track progress, earn stars, and unlock your potential!
          </p>
          <div className="mt-7 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <a
              href="/login"
              className="group inline-flex items-center gap-2 rounded-2xl bg-gray-900 px-5 py-3 text-sm font-semibold text-white shadow-lg hover:bg-gray-800"
            >
              Start Learning <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </a>
            <a
              href="/register"
              className="inline-flex items-center gap-2 rounded-2xl border border-gray-200 bg-white px-5 py-3 text-sm font-semibold text-gray-800 shadow-sm hover:bg-gray-50"
            >
              Join CIFIX <Rocket className="h-4 w-4" />
            </a>
          </div>
        </motion.div>

        {/* Feature cards */}
        <section id="about" className="mx-auto mt-14 grid w-full max-w-5xl grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <FeatureCard
            icon={<BookOpen className="h-5 w-5" />}
            title="Interactive Modules"
            desc="Explore fun lessons with hands-on activities and engaging content."
          />
          <FeatureCard
            icon={<Star className="h-5 w-5" />}
            title="Progress Tracking"
            desc="Earn stars and track your learning journey with detailed progress reports."
          />
          <FeatureCard
            icon={<Users className="h-5 w-5" />}
            title="Parent Dashboard"
            desc="Parents can monitor progress and download comprehensive learning reports."
          />
        </section>

        {/* Features preview */}
        <section id="modules" className="mx-auto mt-16 w-full max-w-5xl">
          <h2 className="text-center text-xl font-bold text-gray-900 sm:text-2xl">What's Inside CIFIX</h2>
          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <FeatureModule 
              icon="📚" 
              title="Learning Modules" 
              desc="Interactive lessons designed for kids"
            />
            <FeatureModule 
              icon="🧪" 
              title="Skills Assessment" 
              desc="Discover your learning style and abilities"
              hasLink={true}
              link="/assessment/start"
            />
            <FeatureModule 
              icon="⭐" 
              title="Star System" 
              desc="Earn stars for completing activities"
            />
            <FeatureModule 
              icon="📊" 
              title="Progress Reports" 
              desc="Track your learning journey over time"
            />
            <FeatureModule 
              icon="👨‍👩‍👧‍👦" 
              title="Parent Portal" 
              desc="Parents can view detailed progress"
              hasLink={true}
              link="/parent"
            />
            <FeatureModule 
              icon="🎯" 
              title="Personal Dashboard" 
              desc="Your own learning hub and activities"
              hasLink={true}
              link="/dashboard"
            />
          </div>
        </section>

        {/* Safety & Access Info */}
        <section id="safety" className="mx-auto mt-16 w-full max-w-4xl">
          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-3xl border border-gray-100 bg-white/70 p-6 shadow-sm backdrop-blur">
              <div className="flex items-start gap-3">
                <div className="mt-1 flex h-9 w-9 items-center justify-center rounded-xl bg-gray-900 text-white">
                  <ShieldCheck className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-gray-900">Safe & Secure</h3>
                  <p className="mt-1 text-sm leading-6 text-gray-600">
                    CIFIX Kids Hub is designed with child safety in mind. Secure access codes, parent oversight, and age-appropriate content.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="rounded-3xl border border-gray-100 bg-white/70 p-6 shadow-sm backdrop-blur">
              <div className="flex items-start gap-3">
                <div className="mt-1 flex h-9 w-9 items-center justify-center rounded-xl bg-gray-900 text-white">
                  <GraduationCap className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-gray-900">Easy Access</h3>
                  <p className="mt-1 text-sm leading-6 text-gray-600">
                    Students use their access code and first name to log in. Parents can view progress with their email and the same access code.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="mx-auto w-full max-w-7xl px-6 pb-12 pt-8 text-sm text-gray-500">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <p>© {new Date().getFullYear()} CIFIX Kids Hub • Safe Learning Platform</p>
          <div className="flex items-center gap-4">
            <a href="/parent" className="hover:text-gray-700">Parent Portal</a>
            <a href="#safety" className="hover:text-gray-700">Safety</a>
            <a href="mailto:support@cifix.com" className="hover:text-gray-700">Support</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, desc }) {
  return (
    <motion.div
      className="group rounded-3xl border border-gray-100 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
      initial={{ opacity: 0, y: 8 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      viewport={{ once: true, margin: "-40px" }}
    >
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gray-900 text-white">
          {icon}
        </div>
        <div className="text-sm font-semibold text-gray-900">{title}</div>
      </div>
      <p className="mt-3 text-sm leading-6 text-gray-600">{desc}</p>
    </motion.div>
  );
}

function FeatureModule({ icon, title, desc, hasLink = false, link = "#" }) {
  const content = (
    <motion.div
      className="relative rounded-3xl border border-gray-100 bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
      initial={{ opacity: 0, y: 8 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      viewport={{ once: true, margin: "-40px" }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="text-3xl">{icon}</div>
        {hasLink && (
          <ArrowRight className="h-4 w-4 text-gray-400 group-hover:text-gray-600 transition-colors" />
        )}
      </div>
      <div className="text-base font-semibold text-gray-900 mb-2">{title}</div>
      <p className="text-sm text-gray-600">{desc}</p>
    </motion.div>
  );

  if (hasLink) {
    return (
      <a href={link} className="group block">
        {content}
      </a>
    );
  }

  return content;
}

function IconChip({ label }) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white/80 px-3 py-1 text-xs font-semibold text-gray-700 shadow-sm backdrop-blur">
      {label}
    </div>
  );
}

function IconBadge({ icon, text }) {
  return (
    <div className="flex items-center gap-2 rounded-2xl border border-gray-200 bg-white/80 px-3 py-1 text-xs font-medium text-gray-700 shadow-sm backdrop-blur">
      {icon}
      <span>{text}</span>
    </div>
  );
}