import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, User } from 'lucide-react';
import profileImg from '../assets/profile.png';
import logoImg from '../assets/logo.png';

const AboutPage = () => {

  const useFadeInOnScroll = () => {
    const ref = useRef(null);
    const [visible, setVisible] = useState(false);
    useEffect(() => {
      const observer = new IntersectionObserver(
        ([entry]) => { if (entry.isIntersecting) setVisible(true); },
        { threshold: 0.15 }
      );
      if (ref.current) observer.observe(ref.current);
      return () => observer.disconnect();
    }, []);
    return { ref, visible };
  };

  const ChatMessage = ({ children, delay = 0 }) => {
    const { ref, visible } = useFadeInOnScroll();
    return (
      <div
        ref={ref}
        style={{ transitionDelay: `${delay}ms` }}
        className={`transition-all duration-700 ease-out ${
          visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'
        }`}
      >
        {children}
      </div>
    );
  };

  const Highlight = ({ text, children }) => (
    <span className="text-[#FF5A5F] font-bold">{children || text}</span>
  );

  const CWAvatar = () => (
    <div className="w-10 h-10 rounded-full bg-[#F3D38D] border-2 border-white shadow-sm flex items-center justify-center flex-shrink-0 mt-1">
      <span className="text-xs font-bold">CW</span>
    </div>
  );

  const CWLabel = () => (
    <span className="text-xs font-bold uppercase mb-2 block text-gray-500">ChatWilly</span>
  );

  const UserBubble = ({ text }) => (
    <div className="flex justify-end">
      <div className="relative w-[80%]">
        <span className="absolute -top-6 right-0 text-xs font-bold uppercase flex items-center gap-1 text-gray-500">
          User <div className="w-5 h-5 rounded-full bg-[#FF5A5F] flex items-center justify-center text-white"><User size={10} /></div>
        </span>
        <div className="bg-white border border-gray-100 shadow-sm p-5 rounded-3xl rounded-tr-sm text-[15px] text-gray-800">{text}</div>
      </div>
    </div>
  );

  const EduCard = ({ title, school, period, grade, highlight }) => (
    <div className="flex flex-col gap-1">
      <h3 className="text-base font-black text-[#1B233A]">{title}</h3>
      <p className="text-sm text-gray-500">{school}</p>
      <div className="flex items-center gap-3 mt-1">
        <span className="text-xs text-gray-400">{period}</span>
        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${highlight ? 'bg-[#F3D38D] text-[#1B233A]' : 'bg-gray-100 text-gray-600'}`}>{grade}</span>
      </div>
    </div>
  );

  const ExpCard = ({ role, company, location, period, bullets, current }) => (
    <div>
      <div className="flex flex-wrap items-center gap-2 mb-1">
        <h3 className="text-base font-black text-[#1B233A]">{role}</h3>
        {current && <span className="text-xs font-bold bg-[#FF5A5F] text-white px-2 py-0.5 rounded-full">Current</span>}
      </div>
      <p className="text-sm font-semibold text-gray-600">{company} <span className="font-normal text-gray-400">· {location}</span></p>
      <p className="text-xs text-gray-400 mb-3">{period}</p>
      <ul className="space-y-1.5">
        {bullets.map((b, i) => (
          <li key={i} className="flex gap-2 text-sm text-gray-600">
            <span className="text-[#FF5A5F] mt-0.5 flex-shrink-0">•</span>{b}
          </li>
        ))}
      </ul>
    </div>
  );

  const SkillGroup = ({ label, tags }) => (
    <div>
      <p className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">{label}</p>
      <div className="flex flex-wrap gap-2">
        {tags.map((t) => (
          <span key={t} className="text-xs font-semibold bg-gray-100 text-gray-700 px-3 py-1 rounded-full">{t}</span>
        ))}
      </div>
    </div>
  );

  return (
    <div className="max-w-5xl mx-auto px-4 py-6 md:py-10 pb-20">
      {/* Header */}
      <header className="flex justify-between items-center mb-8">
        <div className="flex items-center">
          <img
            src={logoImg}
            alt="ChatWilly Logo"
            className="h-12 md:h-16 w-auto object-contain"
          />
        </div>
        <Link to="/" className="text-sm font-semibold flex items-center gap-2 bg-[#FEEBCE] text-[#D4891C] px-4 py-2 rounded-full hover:bg-[#F3D38D] transition-colors">
          <ArrowLeft size={16} /> Back to Chat
        </Link>
      </header>

      {/* Hero Section */}
      <div className="mb-10 md:mb-20">

        {/* Yellow card */}
        <div className="bg-[#F3D38D] rounded-[2.5rem] p-8 md:p-14 relative overflow-hidden flex flex-col md:flex-row shadow-sm">

          {/* Decorative dots */}
          <div className="absolute top-8 left-8 flex gap-2">
            <div className="w-6 h-3 bg-[#FF5A5F] rounded-full opacity-80"></div>
            <div className="w-3 h-3 bg-[#FF5A5F] rounded-full opacity-40"></div>
          </div>

          {/* Mobile: photo + name row */}
          <div className="flex md:hidden items-center gap-5 mt-8 mb-6">
            <div className="w-24 h-24 rounded-full border-4 border-[#FF5A5F] overflow-hidden flex-shrink-0 shadow-md">
              <img src={profileImg} alt="William Simoni" className="w-full h-full object-cover" />
            </div>
            <div>
              <h1 className="text-4xl font-black text-[#1B233A] leading-[1.1] tracking-tight">
                WILLIAM<br/>SIMONI
              </h1>
              <p className="font-bold text-xs tracking-widest text-gray-700 mt-2">AI ENGINEER</p>
            </div>
          </div>

          {/* Desktop: name block */}
          <div className="hidden md:block mt-16 relative z-10 w-1/2">
            <h1 className="text-7xl font-black text-[#1B233A] leading-[1.1] mb-6 tracking-tight">
              WILLIAM<br/>SIMONI
            </h1>
            <p className="font-bold text-sm tracking-widest text-gray-800 mb-2">AI ENGINEER</p>
            <p className="text-xs font-semibold text-gray-600 tracking-wider">
              Software Engineer • Photographer • Video Maker • Thinker
            </p>
          </div>

          {/* Desktop: photo */}
          <div className="hidden md:flex absolute right-10 w-[450px] h-[450px] rounded-full border-[10px] border-[#FF5A5F] flex-shrink-0 overflow-hidden shadow-inner transform rotate-[-5deg]">
            <img src={profileImg} alt="William Simoni" className="w-full h-full object-cover" />
          </div>
        </div>

        {/* Red quote card — inline on mobile, overlapping on desktop */}
        <div className="md:relative md:-mt-10 md:mx-[10%]">
          <div className="bg-[#FF5A5F] text-white p-6 md:p-8 rounded-[2rem] shadow-xl mt-4 md:mt-0 md:w-[60%] md:mx-auto">
            <p className="text-base md:text-xl font-light leading-relaxed">
              I'm <strong className="font-bold">William</strong>. As I always say, I want to be a <em className="italic font-serif text-white/90">Magician</em>. A magician who waves <strong className="font-bold">dreams</strong>, evokes <em className="italic text-white/90">laughs</em> and inspires people to live their <strong className="font-bold">best lives</strong>.
            </p>
          </div>
        </div>

      </div>

      {/* Static Mock Chat */}
      <div className="max-w-2xl mx-auto mt-10 md:mt-24 space-y-10 px-4">

        {/* ── EDUCATION ── */}
        <ChatMessage delay={0}>
          <UserBubble text={<>Tell me about your <Highlight>EDUCATION</Highlight></>} />
        </ChatMessage>
        <ChatMessage delay={150}>
          <div className="flex gap-4 items-start">
            <CWAvatar />
            <div className="flex-1">
              <CWLabel />
              <div className="bg-[#F3D38D] rounded-[2rem] rounded-tl-sm p-6 md:p-8 shadow-sm space-y-5">
                <EduCard title="Bachelor's in Computer Science" school="University of Pisa, Italy" period="2016 – 2020" grade="110/110" />
                <div className="border-t border-black/10" />
                <EduCard title="Master's in Computer Science — AI" school="University of Pisa, Italy" period="2020 – 2024" grade="110/110 cum laude" highlight />
              </div>
            </div>
          </div>
        </ChatMessage>

        {/* ── EXPERIENCE ── */}
        <ChatMessage delay={0}>
          <UserBubble text={<>What about your <Highlight>EXPERIENCE</Highlight>?</>} />
        </ChatMessage>
        <ChatMessage delay={150}>
          <div className="flex gap-4 items-start">
            <CWAvatar />
            <div className="flex-1">
              <CWLabel />
              <div className="bg-[#F3D38D] rounded-[2rem] rounded-tl-sm p-6 md:p-8 shadow-sm space-y-6">
                <ExpCard
                  role="AI Engineer" company="ION Group" location="Pisa, Italy"
                  period="Aug 2024 – Present" current
                  bullets={[
                    "Built multi-agent systems cutting customer service response from months to days.",
                    "Deployed Databricks pipelines for unstructured data, reducing processing from weeks to days.",
                    "Fine-tuned LLMs with LoRA achieving 10–20% accuracy improvement.",
                    "Deployed MCP servers on Kubernetes for org-wide knowledge sharing.",
                    "Deployed LLMs on AWS EC2 via vLLM; built AI dashboards with Streamlit.",
                  ]}
                />
                <div className="border-t border-black/10" />
                <ExpCard
                  role="Software Engineer" company="Iterates" location="Brussels, Belgium"
                  period="Feb 2023 – Aug 2023"
                  bullets={[
                    "Developed backend in C# and frontend in Vue.js for a facility incident management system.",
                    "Designed custom enterprise solutions using Airtable for client integration.",
                  ]}
                />
                <div className="border-t border-black/10" />
                <ExpCard
                  role="Co-founder" company="Iris — AI Startup" location="Retail Theft Detection"
                  period="May 2022 – Aug 2022"
                  bullets={[
                    "Built ML models to detect suspicious behaviour from human skeletal movement.",
                    "Led data collection, prototyping, and legal validation.",
                  ]}
                />
              </div>
            </div>
          </div>
        </ChatMessage>

        {/* ── SKILLS ── */}
        <ChatMessage delay={0}>
          <UserBubble text={<>What are your <Highlight>SKILLS</Highlight>?</>} />
        </ChatMessage>
        <ChatMessage delay={150}>
          <div className="flex gap-4 items-start">
            <CWAvatar />
            <div className="flex-1">
              <CWLabel />
              <div className="bg-[#F3D38D] rounded-[2rem] rounded-tl-sm p-6 md:p-8 shadow-sm space-y-5">
                <SkillGroup label="Languages" tags={["Python", "C#", "JavaScript", "SQL"]} />
                <SkillGroup label="Frameworks & Tools" tags={["PyTorch", "LangChain", "LangGraph", "FastAPI", "Streamlit", "PostgreSQL"]} />
                <SkillGroup label="AI / NLP" tags={["Transformers", "LLM fine-tuning", "Embeddings", "Multi-agent", "Prompt engineering"]} />
                <SkillGroup label="Dev & Ops" tags={["REST APIs", "Git", "CI/CD", "Jenkins", "ArgoCD"]} />
                <SkillGroup label="Languages spoken" tags={["Italian 🇮🇹", "English 🇬🇧", "French 🇫🇷"]} />
              </div>
            </div>
          </div>
        </ChatMessage>

        {/* ── PUBLICATION ── */}
        <ChatMessage delay={0}>
          <UserBubble text={<>Any <Highlight>PUBLICATIONS</Highlight>?</>} />
        </ChatMessage>
        <ChatMessage delay={150}>
          <div className="flex gap-4 items-start">
            <CWAvatar />
            <div className="flex-1">
              <CWLabel />
              <div className="bg-[#1B233A] rounded-[2rem] rounded-tl-sm p-6 md:p-8 text-white shadow-sm">
                <p className="text-xs font-bold tracking-widest text-[#F3D38D] uppercase mb-2">Publication · CoRR 2025</p>
                <h3 className="text-xl font-black mb-3">Learning to Quantify Graph Nodes</h3>
                <p className="text-sm text-white/70 leading-relaxed">
                  Developed <strong className="text-white">XNQ</strong>, a state-of-the-art method for Network Quantification combining randomized recursive GNN embeddings with an EM-based adjustment procedure — achieving <strong className="text-[#F3D38D]">10x–100x speedups</strong> over existing methods.
                </p>
              </div>
            </div>
          </div>
        </ChatMessage>

        {/* ── ORGANISATIONS ── */}
        <ChatMessage delay={0}>
          <UserBubble text={<>Were you part of any <Highlight>ORGANISATIONS</Highlight>?</>} />
        </ChatMessage>
        <ChatMessage delay={150}>
          <div className="flex gap-4 items-start">
            <CWAvatar />
            <div className="flex-1">
              <CWLabel />
              <div className="bg-[#F3D38D] rounded-[2rem] rounded-tl-sm p-6 md:p-8 shadow-sm">
                <ExpCard
                  role="Communication Group Leader" company="Erasmus Student Network"
                  location="Pisa, Italy" period="Sep 2022 – Jul 2024"
                  bullets={[
                    "Led a team of ~15 people managing multimedia content for ESN Pisa's channels.",
                    "Produced videos, Instagram posts/stories, and LinkedIn articles for Erasmus events.",
                    "Coordinated the content calendar and visual direction of the association.",
                  ]}
                />
              </div>
            </div>
          </div>
        </ChatMessage>

      </div>
      {/* Footer */}
      <div className="mt-16 text-center space-y-6">
        <a  href="https://www.linkedin.com/in/william-simoni-2b7127220/"
          target="_blank"
          rel="noopener noreferrer"
        >
          <button className="bg-[#FF5A5F] hover:bg-[#e04e52] transition-colors text-white font-bold py-4 px-8 rounded-full shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all">
            Let's Start a Project
          </button>
        </a>
          <p className="text-[10px] font-bold tracking-[0.2em] text-gray-400 mt-4 uppercase">
            Software Engineer • Photographer • Video Maker • Thinker
          </p>
      </div>

    </div>
  );
};

export default AboutPage;
