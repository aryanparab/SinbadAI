'use client';
import Link from 'next/link';
import AccountButton from './AccountButton';
import { usePathname } from 'next/navigation';
import { ArrowUpRight, Check } from 'lucide-react';
export default function Navbar(){
  const path=usePathname();
  if(path==='/game')return null;
  return <header className="sb-site-header"><Link href="/" className="sb-brand"><span className="sb-monogram">S</span><span>SINBAD<span className="sb-brand-ai"> / AI</span></span></Link><div className="sb-site-links"><span><Check size={12}/>Guest play available</span><AccountButton/><a href="https://github.com/aryanparab/SinbadAI" target="_blank" rel="noreferrer" className="sb-text-link">The project <ArrowUpRight size={13}/></a></div></header>;
}
