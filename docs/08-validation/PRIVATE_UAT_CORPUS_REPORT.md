# Private UAT Corpus API and Batch Report

Generated: 2026-09-03T09:52:52.004272+00:00

## Outcome

- Selected files: 71
- Accepted images: 70
- Skipped non-images: 1
- Individual API processing passes: 70
- Individual API processing failures: 0
- Grouped product API processing passes: 50
- Grouped product API processing failures: 0
- Suggested product groups: 50
- Maximum images in a group: 3
- Functional gate: PASS
- Performance gate: PASS
- Complete gate: PASS
- Equivalent cross-format panel integration: PASS

## Performance

| Scope | Average | Median | P95 | Maximum | Average target | Hard-case target |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Individual images | 3.559 s | 3.378 s | 5.943 s | 6.449 s | PASS | PASS |
| Grouped products | 0.546 s | 0.469 s | 0.892 s | 1.359 s | PASS | PASS |

## Equivalent cross-format panel integration

A content-only scan selected two visually equivalent files with different encodings. The first analysis request after fresh application readiness returned HTTP 200 in 6.015 seconds, retained 2 panel records, and recorded 1 duplicate link. Worker generation was 1 before and 1 after the request.

## Accuracy boundary

This run proves admission, decode, OCR completion, 24-check contract integrity, original-pixel evidence integrity, grouping, product reruns, and latency through the production multipart API. It does not turn label-derived text into an independent application record.

The local oracle contains 50 cases. Exactly 42 current filenames match it, 28 current images are not covered, and 8 oracle filenames are absent. A complete current-corpus human oracle is therefore required before claiming 70-image field-level or legal-label accuracy.

## Per-image production API results

| File | API | Time | Type | Brand | Class/type | ABV | Proof | Net contents | Producer | Origin | Machine finding |
| --- | ---: | ---: | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| 0wLM9.jpg | 200 | 6.443 s | wine | Tuscan | Sangiovese | 13.5 | Not read | 750 mL | Not read | Not read | Review needed |
| 111_Wine_Valle_Front.png | 200 | 4.240 s | wine | VALLE DI PIETRA | Sangiovese | 13.5 | Not read | 750 mL | Not read | Not read | Review needed |
| 222_Silverpine_Wine.png | 200 | 4.232 s | wine | SILVERPINE | PINOT NOIR | 13.2 | Not read | 750 mL | Not read | Not read | Review needed |
| 25e1c2bfd38a40e4ada08da07fcec9d4--modern-vintage-graphic-design-graphic-design-blogs-2987191357.jpg | 200 | 4.566 s | malt_beverage | PEAK FARM | DOUBLE PALE ALE | 7.2 | Not read | 16 fl oz | SYCAMORE BREWING 2161HAWKINS STREET CHARLOTTE.NC 28203 | Not read | Review needed |
| 333_CascadeLight_Wine.png | 200 | 5.049 s | wine | CASCADE LIGHT | RIESLING | 11.5 | Not read | 750 mL | Cascade Light Winery, Watkins Glen New York | Not read | Review needed |
| 3urY2.jpg | 200 | 2.558 s | wine | FOX HOLLOW | RIESLING | 12.0 | Not read | 750 mL | Produced and bottled by Fox Hollow Vincyards, Hammondsport New York. | Not read | Review needed |
| 555_Northveil_Vodka.png | 200 | 5.684 s | distilled_spirits | NORTHVEIL | VODKA | 40.0 | 80.0 | 750 mL | Not read | Not read | Review needed |
| 888SilverPine_Wine.png | 200 | 4.811 s | wine | SILVERPINE | PINOT NOIR | 13.2 | Not read | 750 mL | Not read | Not read | Review needed |
| 8Gf8v.jpg | 200 | 5.906 s | distilled_spirits | CRYSTAL TUNDRA | ed Vodka | 40.0 | 80.0 | 1.75 L | ed and bottled by Distilled and bottled by | Not read | Review needed |
| AnMXl.jpg | 200 | 2.637 s | distilled_spirits | CLEARWATER | BLANCO TEQUILA | 40.0 | 80.0 | 750 mL | Imported by Clearwater Spirits, Austin Teas Hecho en Mexico | Mexico | Review needed |
| BMgMY.jpg | 200 | 3.412 s | Not read | Not read | Not read | Not read | Not read | Not read | Not read | Not read | Review needed |
| bsxs4.jpg | 200 | 2.958 s | wine | MARITIME Mothode Champenoise | Sparkling Wine | 12.5 | Not read | 750 mL | Produced and bottled by Maritime Cellars Mendocino, California | Not read | Review needed |
| Cointeau_Front.jpg | 200 | 3.422 s | distilled_spirits | HARMONIED'ESPRIT D'ECORCES D'ORANGES | LIQUEUR | 40.0 | Not read | 375 mL | Not read | FRANCE-PRODUIT DEFRANCE | Review needed |
| Cointreau_Back.jpg | 200 | 4.354 s | Not read | COUNIN | Not read | Not read | Not read | Not read | IMPORTED BY REMY COINTREAU USA INC. NEW YORKNY | FRANCE | Review needed |
| coTpD.jpg | 200 | 3.667 s | Not read | Not read | Not read | Not read | Not read | Not read | Not read | Not read | Review needed |
| DDqT2.jpg | 200 | 3.023 s | Not read | Not read | Not read | Not read | Not read | Not read | Not read | Not read | Review needed |
| DmK94.jpg | 200 | 3.266 s | Not read | Not read | Not read | Not read | Not read | Not read | Not read | Not read | Review needed |
| EqTB7.jpg | 200 | 2.765 s | Not read | Imoported by Smoke & Agave Imports | Not read | 45.0 | 90.0 | 750 mL | Imoported by Smoke & Agave Imports Imported by Smoke &Agave Imports Los Angeles, California | Mexico | Review needed |
| Gemini_Generated_Image_auilqqauilqqauil (1).jpg | 200 | 2.948 s | distilled_spirits | OTANIST'S | London Dry Gin | 47.0 | 94.0 | 1 L | Not read | Not read | Review needed |
| GuCzO.jpg | 200 | 5.913 s | distilled_spirits | FERRY GOLDENR | RUM | 40.0 | 80.0 | 750 mL | Not read | Barbados | Review needed |
| iFZ0Q.jpg | 200 | 2.702 s | distilled_spirits | BLACKBIRD RESERVE | Kentucky Straight Bourbon Whiskey | 45.0 | 90.0 | 750 mL | Distilled and bottled by Blackbird Disuilling Co. Distilled and botted by Blackbird Dsilling Co. Frankfort, Kentucky | Not read | Review needed |
| J3YuX.jpg | 200 | 3.848 s | malt_beverage | IRON ANCHOR BREWING CO. | INDIA PALE ALE | 7.2 | Not read | 16 fl oz | BREWED AND BOTTLED BY IRON ANCHOR BREWING CO. PORTLAND, MAINE | Not read | Review needed |
| JackDaniels_Back.jpg | 200 | 6.449 s | Not read | JACK DANIEL DISTILLERY | Not read | Not read | Not read | Not read | DISTILLED AND BOTTLED BY JACK DANIEL DISTILLERY LYNCHBURG,TENNESSEE,USA | Not read | Differences detected |
| JackDaniels_Front.jpg | 200 | 3.344 s | distilled_spirits | JACK DANIEL'S | WHISKEY | 40.0 | 80.0 | 375 mL | Not read | Not read | Review needed |
| jsP3W.jpg | 200 | 2.447 s | malt_beverage | MIDNIGHT FORGE | Imperial Oatmeal Stout | 9.5 | Not read | 12 fl oz | Brewed and bottled by Midnight Forge Brewing, Milwaukee, Wisconsin | Not read | Review needed |
| leTeL.jpg | 200 | 3.512 s | wine | IRON CREEK CELLARS | Pinot Noir | 13.8 | Not read | 750 mL | PRODUCED AND BOTTLED BY IRON CREEK CELLARS | Not read | Review needed |
| MXteB.jpg | 200 | 4.893 s | malt_beverage | SUN DOCK | HEAT ALE | 5.0 | Not read | 16 fl oz | un Dock Brewing. ifornia | Not read | Review needed |
| O0P0Z.jpg | 200 | 2.686 s | wine | CEDAR BEND | Chardonnay | 13.5 | Not read | 750 mL | Produced and bottled by Cedar Bend Vincyards Oregon. | Not read | Review needed |
| PtNj9.jpg | 200 | 2.521 s | distilled_spirits | BOTANIST'S SECRET | London Dry Gin | 47.0 | 94.0 | 1 L | Distilled &bottled by Botanist's Secret Distilley Lonon. Botanist's Secret Distillery, London. seDy.ondon | Not read | Review needed |
| RevolverBrewing.jpg | 200 | 0.190 s | malt_beverage | BLOOD & HONEY | TEXAS STYLE ALE | Not read | Not read | Not read | REVOLVER BREWING LITTLETON, CO | Not read | Review needed |
| RevolverBrewing.png | 200 | 4.422 s | malt_beverage | BLOOD & HONEY | TEXAS STYLE ALE | Not read | Not read | Not read | REVOLVER BREWING LITTLETON, CO | Not read | Review needed |
| Test_TTB_Image_0001.jpg | 200 | 4.408 s | wine | STONE'S THROW | Valley Cabernet Sauvignon | 14.5 | Not read | 750 mL | Produced and bottled by Stone's Throw. Vineyards, Napa, California. | Not read | Review needed |
| Test_TTB_Image_0002.jpg | 200 | 4.273 s | distilled_spirits | DISTILLEDFROM GRAIN | VODKA | 40.0 | 80.0 | 750 mL | Distilled and bottled by Northwind. | Not read | Differences detected |
| Test_TTB_Image_0003.jpg | 200 | 2.814 s | distilled_spirits | RED MESA | REPOSADO TEQUILA | 38.0 | 76.0 | 750 mL | Imported by Red Mesa Imports, San Antonio, Texas. Hecho en Mexico. | Mexico | Differences detected |
| Test_TTB_Image_0004.jpg | 200 | 2.047 s | distilled_spirits | CRYSTAL TUNDRA | Distilled Vodka | 40.0 | 80.0 | 1.75 L | Distilled and bottled by Distiled and bottled by | Not read | Review needed |
| Test_TTB_Image_0005.jpg | 200 | 3.183 s | distilled_spirits | BOTANIST'S SECRET | LONDON DRY GIN | 47.0 | 94.0 | 1 L | Distilled & bottled by. Botanist's Secret Distillery, London. | Not read | Review needed |
| Test_TTB_Image_0006.jpg | 200 | 2.083 s | distilled_spirits | BOTANIST'S SECRET | LONDON DRY GIN | 47.0 | 94.0 | 1 L | Distilled & bottled by. Botanist's Secret Distillery, London. | Not read | Review needed |
| Test_TTB_Image_0007.jpg | 200 | 2.559 s | malt_beverage | NIGHT FORGE | IMPERIAL OATMEAL STOUT | 9.5 | Not read | Not read | Brewed and bottled by Midnight Forge Brewing Milwaukee, Wisconsin | Not read | Review needed |
| Test_TTB_Image_0008.jpg | 200 | 2.746 s | Not read | Not read | Not read | Not read | Not read | Not read | Not read | Not read | Review needed |
| Test_TTB_Image_0009.jpg | 200 | 2.669 s | malt_beverage | IRON ANCHOR BREWING CO. | INDIA PALE ALE | 7.2 | Not read | 16 fl oz | Brewed and bottled by Iron Anchor Brewing Co., Portland, Maine. | Not read | Review needed |
| Test_TTB_Image_0011.jpg | 200 | 0.172 s | distilled_spirits | OTANIST'S | London Dry Gin | 47.0 | 94.0 | 1 L | Not read | Not read | Review needed |
| Test_TTB_Image_0021.jpg | 200 | 3.617 s | distilled_spirits | BLACKBIRD RESERVE | KENTUCKYSTRAIGHT BOURBON WHISKEY | 45.0 | 90.0 | 750 mL | Distilled & bottled by Blackbird Distilling Co.,. Bardstown, Kentucky | Not read | Review needed |
| Test_TTB_Image_0022.jpg | 200 | 2.847 s | distilled_spirits | BLACKBIRD RESERVE | KENTUCKYSTRAIGHT BOURBON WHISKEY | 45.0 | 90.0 | 750 mL | Distilled & bottled by Blackbird Distilling Co.,. Bardstown, Kentucky | Not read | Review needed |
| Test_TTB_Image_0023.jpg | 200 | 3.544 s | wine | MARITIME | SPARKLING WINE | 12.5 | Not read | 750 mL | Produced and bottled by Maritime Cellars, Mendocino, California FRONT /BRAND LABEL | Not read | Review needed |
| Test_TTB_Image_0024.jpg | 200 | 5.015 s | wine | FROST RIDGE | Wine of New Zealand | 12.0 | Not read | 750 mL | ported by Frost Ridge Imports, Seattle, Washingt Imported by Frost Ridge Imports, Seattle, Washington.. | New Zealand | Review needed |
| Test_TTB_Image_0025.jpg | 200 | 1.911 s | distilled_spirits | BLACKBIRD RESERVE | Kentucky Straight Bourbon Whiskey | 45.0 | 90.0 | 750 mL | Distilled and bottled by Blackbird Disuilling Co. Distilled and botted by Blackbird Dsilling Co. Frankfort, Kentucky | Not read | Review needed |
| Test_TTB_Image_0026.jpg | 200 | 2.990 s | malt_beverage | IRON ANCHOR BREWING CO. | INDIA PALE ALE | 7.2 | Not read | 16 fl oz | BREWED AND BOTTLED BY IRON ANCHOR BREWING CO. PORTLAND, MAINE | Not read | Review needed |
| Test_TTB_Image_0027.jpg | 200 | 3.054 s | distilled_spirits | CLEARWATER | BLANCO TEQUILA | 40.0 | 80.0 | 750 mL | Imported by Clearwater Spirits, Austin, Texas Hecho en Mexico. | Mexico | Review needed |
| Test_TTB_Image_0028.jpg | 200 | 1.911 s | malt_beverage | MIDNIGHT FORGE | Imperial Oatmeal Stout | 9.5 | Not read | 12 fl oz | Brewed and bottled by Midnight Forge Brewing, Milwaukee, Wisconsin | Not read | Review needed |
| Test_TTB_Image_0029.jpg | 200 | 3.835 s | wine | FOX HOLLOW | RIESLING | 12.0 | Not read | 750 mL | Produced and bottled by Fox Hollow Vineyards, Hammondsport, New York | Not read | Review needed |
| Test_TTB_Image_0030.jpg | 200 | 2.217 s | wine | CEDAR BEND | Chardonnay | 13.5 | Not read | 750 mL | Produced and bottled by Cedar Bend Vincyards Oregon. | Not read | Review needed |
| Test_TTB_Image_0031.jpg | 200 | 2.969 s | malt_beverage | HARBOR LIGHTSE | PALE ALE | 5.2 | Not read | 12 fl oz | Brewed and bottled by Harbor Lights. Brewing Co., Seattle, Washington | Not read | Review needed |
| Test_TTB_Image_0032.jpg | 200 | 1.982 s | distilled_spirits | BOTANIST'S SECRET | London Dry Gin | 47.0 | 94.0 | 1 L | Distilled &bottled by Botanist's Secret Distilley Lonon. Botanist's Secret Distillery, London. seDy.ondon | Not read | Review needed |
| Test_TTB_Image_0033.jpg | 200 | 4.065 s | Not read | Not read | Not read | Not read | Not read | Not read | Not read | Not read | Review needed |
| Test_TTB_Image_0034.jpg | 200 | 3.229 s | wine | IRON CREEK | WILLAMETTE VALLEY PINOT NOIR | 13.8 | Not read | 750 mL | Produced and bottled by Iron Creek Cellars, McMinnville, Oregon | Not read | Review needed |
| Test_TTB_Image_0035.jpg | 200 | 3.179 s | wine | WHISPERING PINES ESTATE | CALIFORNIA CABERNET SAUVIGNON | 13.5 | Not read | 750 mL | Produced and bottled by Whispering Pines Estate, Napa, California | Not read | Review needed |
| Test_TTB_Image_0036.jpg | 200 | 4.584 s | distilled_spirits | LUN | REPOSADO TEQUILA | 40.0 | 80.0 | 750 mL | Imported by Casa de Luna Spirits, Houston, Texas Hecho en Mexico. | Mexico | Review needed |
| Test_TTB_Image_0037.jpg | 200 | 3.045 s | distilled_spirits | BOTANIST'S SECRET | . LONDON DRY GIN | 47.0 | 94.0 | 1 L | Distilled & bottled by Botanist's Secret Distillery, London | Not read | Review needed |
| Test_TTB_Image_0038.jpg | 200 | 4.525 s | malt_beverage | Not read | Pale Ale | 5.2 | Not read | 12 fl oz | Not read | Not read | Review needed |
| Test_TTB_Image_0039.jpg | 200 | 6.140 s | wine | ted by Whisperiog Pines Esulc | Cabernet Sauvignon | 13.5 | Not read | 750 mL | Podoced and bottled by Whisperiog Pites Esulc ted by Whisperiog Pines Esulc Napa, Califocnia | Not read | Review needed |
| Test_TTB_Image_0040.jpg | 200 | 4.713 s | distilled_spirits | CASA DE LUNA | 100% Blue Agave Reposado Tequila | 40.0 | 80.0 | 750 mL | Not read | Mexico | Review needed |
| Test_TTB_Image_0041.jpg | 200 | 3.589 s | distilled_spirits | CRYSTAL TUNDRA | DISTILLED VODKA | 40.0 | 80.0 | 1.75 L | Distilled and bottled by Crystal Tundra Spirits, Anchorage, Alaska | Not read | Review needed |
| Test_TTB_Image_0042.jpg | 200 | 2.650 s | distilled_spirits | OLD FERRY | AGED RUM | 40.0 | 80.0 | 1 L | Distilled and bottled by Old Ferry Rum Co. Charleston, South Carolina | Not read | Differences detected |
| uqgyU.jpg | 200 | 3.620 s | malt_beverage | HARBOR LIGHTS | Pale Ale | 5.2 | Not read | 12 fl oz | Not read | Not read | Review needed |
| Vodka_Back.jpg | 200 | 4.644 s | distilled_spirits | ORGANIC | 100%NEUTRAL SPIRITS DISTILLED | Not read | Not read | Not read | BY HAWAII SEA SPIRITS LLC | Not read | Review needed |
| Vodka_Front.jpg | 200 | 3.192 s | Not read | OrganicVodka | Not read | 40.0 | 80.0 | 750 mL | Not read | Not read | Review needed |
| wKE1J.jpg | 200 | 4.570 s | wine | ted by Whisperiog Pines Esulc | Cabernet Sauvignon | 13.5 | Not read | 750 mL | Podoced and bottled by Whisperiog Pites Esulc ted by Whisperiog Pines Esulc Napa, Califocnia | Not read | Review needed |
| XjPpA.jpg | 200 | 3.457 s | distilled_spirits | CASA DE LUNA | 100% Blue Agave Reposado Tequila | 40.0 | 80.0 | 750 mL | Not read | Mexico | Review needed |
| XXL_Back.jpg | 200 | 2.275 s | wine | STRAWBERRY | GRAPE WINE WITH NATURAL FLA | 16.0 | Not read | 750 mL | Not read | Not read | Review needed |
| XXL_Front.jpg | 200 | 5.943 s | Not read | strawberries | Not read | 16.0 | Not read | Not read | Not read | Not read | Review needed |
