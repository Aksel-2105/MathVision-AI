import { ArrowLeft, Construction } from "lucide-react";
import { Link } from "react-router-dom";

type PhasePlaceholderPageProps = { title: string; phase: string; description: string };

export function PhasePlaceholderPage({ title, phase, description }: PhasePlaceholderPageProps) { return <section className="mx-auto flex min-h-[60vh] max-w-3xl items-center justify-center"><div className="w-full rounded-2xl border border-line bg-surface p-8 text-center shadow-card sm:p-12"><div className="mx-auto grid size-14 place-items-center rounded-2xl bg-cyan/10 text-cyan"><Construction size={26} /></div><p className="eyebrow mt-6">{phase} · Planned</p><h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">{title}</h1><p className="mx-auto mt-4 max-w-xl leading-7 text-ink-muted">{description}</p><Link className="secondary-button mx-auto mt-8 w-fit" to="/"><ArrowLeft size={17} />Back to home</Link></div></section>; }
