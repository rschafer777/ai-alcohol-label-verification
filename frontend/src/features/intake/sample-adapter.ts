import { z } from "zod";

import { profileId } from "../../api/generated-contract";
import type { LoadedSample, SampleAdapter, SamplePackage } from "../../contracts/types";

const referenceSchema = z.object({
  profileId: z.literal(profileId),
  beverageType: z.enum(["malt_beverage", "wine", "distilled_spirits"]),
  referenceProvenance: z.enum(["label_ocr", "manual", "manifest", "sample"]),
  caseLabel: z.string().max(80).nullable().optional(),
  brandName: z.string().min(1).max(160),
  classType: z.string().min(1).max(240),
  abvPercent: z.number().positive().max(100),
  proof: z.number().nonnegative().nullable().optional(),
  netContentsValue: z.number().positive(),
  netContentsUnit: z.enum(["mL", "L"]),
  producerNameAddress: z.string().min(1).max(500),
  isImported: z.boolean(),
  countryOfOrigin: z.string().max(80).nullable().optional(),
  wineAppellation: z.string().max(160).nullable().optional(),
  wineSulfiteStatus: z.enum(["present", "not_present", "unknown"]),
  maltAlcoholSource: z.enum(["added_ingredients", "none", "unknown"]),
});

const sampleSchema = z.object({
  reference: referenceSchema,
  panels: z
    .array(
      z.object({
        panelId: z.string().regex(/^panel-[1-3]$/),
        label: z.string().min(1),
        fileName: z.string().min(1),
        mimeType: z.enum(["image/jpeg", "image/png", "image/webp"]),
        url: z.string().min(1),
      }),
    )
    .min(1)
    .max(3),
});

export function createSampleAdapter(fetcher: typeof fetch = fetch): SampleAdapter {
  return {
    async load(signal?: AbortSignal): Promise<LoadedSample> {
      const manifestResponse = await fetcher("/api/v1/samples/distilled-spirits-v1", {
        signal,
        headers: { Accept: "application/json" },
      });
      if (!manifestResponse.ok) throw new Error("The built-in sample is unavailable.");
      const sample = sampleSchema.parse((await manifestResponse.json()) as SamplePackage);
      const panels = await Promise.all(
        sample.panels.map(async (panel) => {
          const response = await fetcher(panel.url, { signal });
          if (!response.ok) throw new Error("A built-in sample panel is unavailable.");
          const blob = await response.blob();
          return new File([blob], panel.fileName, { type: panel.mimeType });
        }),
      );
      return { reference: sample.reference, panels };
    },
  };
}
