import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, User } from 'lucide-react';
import profileImg from '../assets/profile.png';

const AboutPage = () => {
  return (
    <div className="max-w-5xl mx-auto px-4 py-6 md:py-10 pb-20">
      {/* Header */}
      <header className="flex justify-between items-center mb-8">
        <div className="flex items-center gap-3 font-bold text-lg">
          <div className="w-8 h-8 rounded-full bg-[#F3D38D] flex items-center justify-center text-xs">WS</div>
          William Simoni
        </div>
        <Link to="/" className="text-sm font-semibold flex items-center gap-2 bg-[#FEEBCE] text-[#D4891C] px-4 py-2 rounded-full hover:bg-[#F3D38D] transition-colors">
          <ArrowLeft size={16} /> Back to Chat
        </Link>
      </header>

      {/* Hero Section */}
      <div className="relative mb-32 md:mb-20">
        <div className="bg-[#F3D38D] rounded-[2.5rem] p-8 md:p-14 min-h-[350px] relative overflow-hidden flex flex-col md:flex-row shadow-sm">
          <div className="absolute top-8 left-8 flex gap-2">
            <div className="w-6 h-3 bg-[#FF5A5F] rounded-full opacity-80"></div>
            <div className="w-3 h-3 bg-[#FF5A5F] rounded-full opacity-40"></div>
          </div>
          <div className="mt-10 md:mt-16 relative z-10 w-full md:w-1/2">
            <h1 className="text-5xl md:text-7xl font-black text-[#1B233A] leading-[1.1] mb-6 tracking-tight">
              WILLIAM<br/>SIMONI
            </h1>
            <p className="font-bold text-sm tracking-widest text-gray-800 mb-2">AI ENGINEER</p>
            <p className="text-xs font-semibold text-gray-600 tracking-wider">
              Software Engineer • Photographer • Video Maker • Thinker
            </p>
          </div>
          <div className="absolute -right-20 -top-20 md:right-10 md:top-auto md:relative w-[300px] h-[300px] md:w-[400px] md:h-[400px] rounded-full border-[10px] border-[#FF5A5F] flex-shrink-0 overflow-hidden hidden sm:flex shadow-inner transform rotate-[-5deg]">
            <img src={profileImg} alt="William Simoni" className="w-full h-full object-cover" />
          </div>
        </div>
        <div className="bg-[#FF5A5F] text-white p-6 md:p-8 rounded-[2rem] w-[90%] md:w-[60%] absolute -bottom-16 md:-bottom-10 left-[5%] md:left-[10%] shadow-xl z-20">
          <p className="text-lg md:text-xl font-light leading-relaxed">
            I'm <strong className="font-bold">William</strong>. As I always say, I want to be a <em className="italic font-serif text-white/90">Magician</em>. A magician who waves <strong className="font-bold">dreams</strong> evokes <em className="italic text-white/90">laughs</em> and inspires people to live their <strong className="font-bold">best lives</strong>.
          </p>
        </div>
      </div>

      {/* Static Mock Chat — Education */}
      <div className="max-w-2xl mx-auto mt-24 space-y-8 px-4">
        <div className="flex gap-4 items-start">
          <div className="w-10 h-10 rounded-full bg-[#F3D38D] border-2 border-white shadow-sm flex items-center justify-center flex-shrink-0 mt-1">
            <span className="text-xs font-bold">CW</span>
          </div>
          <div>
            <span className="text-xs font-bold uppercase mb-1 block">ChatWILLY</span>
            <p className="text-[15px] text-gray-800">Hi there! What brings you here?</p>
          </div>
        </div>
        <div className="flex justify-end gap-4 items-start w-full">
          <div className="bg-[#FEEBCE] p-5 rounded-3xl rounded-tr-sm relative w-[80%]">
            <span className="absolute -top-6 right-0 text-xs font-bold uppercase flex items-center gap-1 text-gray-500">
              User <div className="w-5 h-5 rounded-full bg-[#FF5A5F] flex items-center justify-center text-white"><User size={10} /></div>
            </span>
            <p className="text-[15px] text-gray-800">Hi ChatWILLY. Could you tell me about your <span className="text-[#FF5A5F] font-bold">EDUCATION</span> background?</p>
          </div>
        </div>
      </div>

      {/* Education Card */}
      <div className="max-w-3xl mx-auto mt-12 bg-white rounded-[2rem] p-6 md:p-10 shadow-sm border border-gray-100/50">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-full bg-[#F3D38D] border-2 border-white shadow-sm flex items-center justify-center">
            <span className="text-xs font-bold">CW</span>
          </div>
          <div>
            <span className="text-sm font-bold uppercase block">ChatWILLY</span>
            <p className="text-sm text-gray-500">Sure! I have a:</p>
          </div>
        </div>
        <div className="relative pl-6 space-y-10 before:absolute before:inset-0 before:ml-[11px] before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gray-100">
          <div className="relative">
            <div className="absolute left-[-29px] w-3 h-3 bg-[#FF5A5F] rounded-full border-2 border-white top-2"></div>
            <h3 className="text-xl font-black text-[#1B233A] mb-1">Bachelor in Computer Science</h3>
            <p className="text-gray-600 mb-1">University of Pisa, Pisa, Italy</p>
            <p className="text-gray-500 text-sm">Graduated with <strong className="text-black text-base">110</strong></p>
          </div>
          <div className="relative">
            <div className="absolute left-[-29px] w-3 h-3 bg-[#FF5A5F] rounded-full border-2 border-white top-2"></div>
            <h3 className="text-xl font-black text-[#1B233A] mb-1">Master in Computer Science (Artificial Intelligence)</h3>
            <p className="text-gray-600 mb-1">University of Pisa, Pisa, Italy</p>
            <p className="text-gray-500 text-sm">Graduated with <strong className="text-black text-base">110 cum laude</strong></p>
          </div>
        </div>
      </div>

      {/* Mock Chat — Experience */}
      <div className="max-w-2xl mx-auto mt-12 space-y-8 px-4">
        <div className="flex justify-end gap-4 items-start w-full">
          <div className="bg-[#FEEBCE] p-5 rounded-3xl rounded-tr-sm relative w-[80%]">
            <span className="absolute -top-6 right-0 text-xs font-bold uppercase flex items-center gap-1 text-gray-500">
              User <div className="w-5 h-5 rounded-full bg-[#FF5A5F] flex items-center justify-center text-white"><User size={10} /></div>
            </span>
            <p className="text-[15px] text-gray-800">What about your <span className="text-[#FF5A5F] font-bold">EXPERIENCE</span>?</p>
          </div>
        </div>
      </div>

      {/* Experience Card */}
      <div className="max-w-3xl mx-auto mt-6 bg-white rounded-[2rem] p-6 md:p-10 shadow-sm border border-gray-100/50">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-full bg-[#F3D38D] border-2 border-white shadow-sm flex items-center justify-center">
            <span className="text-xs font-bold">CW</span>
          </div>
          <div>
            <span className="text-sm font-bold uppercase block">ChatWILLY</span>
            <p className="text-sm text-gray-500">Here's what I've been building:</p>
          </div>
        </div>
        <div className="relative pl-6 space-y-10 before:absolute before:inset-0 before:ml-[11px] before:h-full before:w-0.5 before:bg-gray-100">

          {/* ION Group */}
          <div className="relative">
            <div className="absolute left-[-29px] w-3 h-3 bg-[#FF5A5F] rounded-full border-2 border-white top-2"></div>
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <h3 className="text-xl font-black text-[#1B233A]">AI Engineer</h3>
              <span className="text-xs font-bold bg-[#F3D38D] px-2 py-0.5 rounded-full">Current</span>
            </div>
            <p className="text-gray-600 font-semibold mb-1">ION Group — Pisa, Italy</p>
            <p className="text-gray-400 text-xs mb-3">Aug 2024 – Present</p>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex gap-2"><span className="text-[#FF5A5F] mt-1">•</span>Built multi-agent systems that cut customer service response time from months to days.</li>
              <li className="flex gap-2"><span className="text-[#FF5A5F] mt-1">•</span>Deployed data pipelines on Databricks for unstructured data, reducing processing from weeks to days.</li>
              <li className="flex gap-2"><span className="text-[#FF5A5F] mt-1">•</span>Fine-tuned small language models with LoRA achieving 10–20% accuracy improvement.</li>
              <li className="flex gap-2"><span className="text-[#FF5A5F] mt-1">•</span>Deployed MCP servers on Kubernetes for org-wide knowledge base sharing.</li>
              <li className="flex gap-2"><span className="text-[#FF5A5F] mt-1">•</span>Deployed LLMs on AWS EC2 using vLLM and built AI dashboards with Streamlit.</li>
            </ul>
          </div>

          {/* Iterates */}
          <div className="relative">
            <div className="absolute left-[-29px] w-3 h-3 bg-[#FF5A5F] rounded-full border-2 border-white top-2"></div>
            <h3 className="text-xl font-black text-[#1B233A] mb-1">Software Engineer</h3>
            <p className="text-gray-600 font-semibold mb-1">Iterates — Brussels, Belgium</p>
            <p className="text-gray-400 text-xs mb-3">Feb 2023 – Aug 2023</p>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex gap-2"><span className="text-[#FF5A5F] mt-1">•</span>Developed backend in C# and frontend in Vue.js for a facility incident management system.</li>
              <li className="flex gap-2"><span className="text-[#FF5A5F] mt-1">•</span>Designed custom enterprise solutions using Airtable for client system integration.</li>
            </ul>
          </div>

          {/* Iris */}
          <div className="relative">
            <div className="absolute left-[-29px] w-3 h-3 bg-[#F3D38D] rounded-full border-2 border-white top-2"></div>
            <h3 className="text-xl font-black text-[#1B233A] mb-1">Co-founder — Iris</h3>
            <p className="text-gray-600 font-semibold mb-1">AI Startup · Retail Theft Detection</p>
            <p className="text-gray-400 text-xs mb-3">May 2022 – Aug 2022</p>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex gap-2"><span className="text-[#FF5A5F] mt-1">•</span>Built ML models to detect suspicious behaviour from human skeletal movement in surveillance footage.</li>
              <li className="flex gap-2"><span className="text-[#FF5A5F] mt-1">•</span>Led data collection, prototyping and legal validation.</li>
            </ul>
          </div>

        </div>
      </div>

      {/* Publication */}
      <div className="max-w-3xl mx-auto mt-6 bg-[#1B233A] rounded-[2rem] p-6 md:p-8 text-white">
        <p className="text-xs font-bold tracking-widest text-[#F3D38D] uppercase mb-2">Publication · 2025</p>
        <h3 className="text-xl font-black mb-2">Learning to Quantify Graph Nodes</h3>
        <p className="text-sm text-white/70 leading-relaxed">Developed XNQ, a state-of-the-art method for Network Quantification combining randomized recursive GNN embeddings with an EM-based adjustment procedure — achieving 10x–100x speedups over existing methods.</p>
        <p className="text-xs text-white/40 mt-3">CoRR</p>
      </div>

      {/* Footer */}
      <div className="mt-16 text-center space-y-6">
        <button className="bg-[#FF5A5F] hover:bg-[#e04e52] transition-colors text-white font-bold py-4 px-8 rounded-full shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all">
          Let's Start a Project
        </button>
        <p className="text-xs text-gray-400 font-medium">© 2024 William Simoni. All Rights Reserved.</p>
      </div>

    </div>
  );
};

export default AboutPage;
