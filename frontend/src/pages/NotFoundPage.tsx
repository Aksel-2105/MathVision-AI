import { ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

export function NotFoundPage() { return <div className="grid min-h-screen place-items-center bg-page p-6"><div className="text-center"><p className="eyebrow">404 · Not found</p><h1 className="mt-3 text-3xl font-semibold text-ink">This route does not exist.</h1><Link className="secondary-button mx-auto mt-6 w-fit" to="/"><ArrowLeft size={17} />Return home</Link></div></div>; }
