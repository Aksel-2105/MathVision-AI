declare module "react-katex" {
  import type { ComponentType } from "react";

  type MathProps = { math: string; errorColor?: string; throwOnError?: boolean };

  export const BlockMath: ComponentType<MathProps>;
  export const InlineMath: ComponentType<MathProps>;
}
