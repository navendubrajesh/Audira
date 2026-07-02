import type { NextConfig } from "next";
import path from "node:path";

const studioSrc = path.join(__dirname, "../studio/src");
const monorepoRoot = path.join(__dirname, "../..");

const nextConfig: NextConfig = {
  transpilePackages: ["@audira/design-tokens", "@audira/studio"],
  outputFileTracingRoot: monorepoRoot,
  webpack: (config) => {
    config.module.rules.push({
      test: /\.tsx?$/,
      include: [studioSrc],
      resolve: {
        alias: {
          "@studio": studioSrc,
        },
      },
    });
    config.resolve.alias = {
      ...config.resolve.alias,
      "@studio": studioSrc,
    };
    return config;
  },
};

export default nextConfig;
