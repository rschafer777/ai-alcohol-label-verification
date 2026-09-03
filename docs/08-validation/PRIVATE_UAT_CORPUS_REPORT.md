# Private UAT Corpus API and Batch Report

Generated: 2026-09-03T17:01:53.743067+00:00

## Outcome

- Selected files: 73
- Accepted images: 71
- Skipped non-images: 2
- Individual API processing passes: 71
- Individual API processing failures: 0
- Grouped product API processing passes: 45
- Grouped product API processing failures: 0
- Suggested product groups: 45
- Maximum images in a group: 3
- Functional gate: PASS
- Performance gate: PASS
- Complete gate: PASS
- Equivalent cross-format panel integration: PASS

## Performance

| Scope | Average | Median | P95 | Maximum | Average target | Hard-case target |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Individual images | 3.456 s | 3.425 s | 4.926 s | 6.434 s | PASS | PASS |
| Grouped products | 0.798 s | 0.523 s | 1.600 s | 4.159 s | PASS | PASS |

## Equivalent cross-format panel integration

A content-only scan selected two visually equivalent files with different encodings. The first analysis request after fresh application readiness returned HTTP 200 in 6.247 seconds, retained 2 panel records, and recorded 1 duplicate link. Worker generation was 1 before and 1 after the request.

## Accuracy boundary

This run proves admission, decode, OCR completion, 24-check contract integrity, original-pixel evidence integrity, grouping, product reruns, and latency through the production multipart API. It does not turn label-derived text into an independent application record.

The local oracle contains 50 cases. Exactly 42 current filenames match it, 29 current images are not covered, and 8 oracle filenames are absent. A complete current-corpus human oracle is therefore required before claiming 70-image field-level or legal-label accuracy.

## Per-image production API results

| File | API | Time | Type | Brand | Class/type | ABV | Proof | Net contents | Producer | Origin | Machine finding |
| --- | ---: | ---: | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| 0wLM9.jpg | 200 | 4.406 s | wine | VALLE DI PIETRA | Sangiovese | 13.5 | Not read | 750 mL | Not read | Italy | Review needed |
| 111_Wine_Valle_Front.png | 200 | 3.671 s | wine | VALLE DI PIETRA | Sangiovese | 13.5 | Not read | 750 mL | Not read | Italy | Review needed |
| 222_Silverpine_Wine.png | 200 | 3.978 s | wine | SILVERPINE | PINOT NOIR | 13.2 | Not read | 750 mL | Not read | Not read | Review needed |
| 25e1c2bfd38a40e4ada08da07fcec9d4--modern-vintage-graphic-design-graphic-design-blogs-2987191357.jpg | 200 | 6.434 s | malt_beverage | PEAK FARM | DOUBLE PALE ALE | Not read | Not read | 16 fl oz | SYCAMORE BREWING 2161HAWKINS STREET CHARLOTTE.NC 28203 | Not read | Review needed |
| 333_CascadeLight_Wine.png | 200 | 4.926 s | wine | CASCADE LIGHT | RIESLING | 11.5 | Not read | 750 mL | Vinted and Bortled by Cascade Light Winery, Watkins Glen New York | Not read | Review needed |
| 3urY2.jpg | 200 | 2.469 s | wine | FOX HOLLOW | RIESLING | 12.0 | Not read | 750 mL | Produced and bottled by Fox Hollow Vincyards, Hammondsport, New York. | Not read | Review needed |
| 555_Northveil_Vodka.png | 200 | 4.574 s | distilled_spirits | NORTHVEIL | VODKA | 40.0 | 80.0 | 750 mL | Distilled and Bottled by Northveil Spirits, Portland, Oregon | Not read | Review needed |
| 888SilverPine_Wine.png | 200 | 4.273 s | wine | SILVERPINE | Not read | 13.2 | Not read | 750 mL | Not read | Not read | Review needed |
| 8Gf8v.jpg | 200 | 4.360 s | distilled_spirits | CRYSTAL TUNDRA | Distilled Vodka | 40.0 | 80.0 | 1.75 L | Distilled and bottled by Crystal Tundra Spirits, Anchorage, Alaska | Not read | Review needed |
| AnMXl.jpg | 200 | 2.858 s | distilled_spirits | CLEARWATER | BLANCO TEQUILA | 40.0 | 80.0 | 750 mL | Imported by Clearwater Spirits, Austin, Texas Hecho en Mexico | Mexico | Review needed |
| BMgMY.jpg | 200 | 3.895 s | wine | MIRROR LAKE | WILLAMETTE VALLEY PINOT GRIS | 12.8 | Not read | 750 mL | Produced and bottled by Miror Lake VineyardsDundee.Oregon | Not read | Review needed |
| bsxs4.jpg | 200 | 5.222 s | wine | MARITIME | SPARKLING WINE | 12.5 | Not read | 750 mL | Not read | Not read | Review needed |
| Cointeau_Front.jpg | 200 | 3.956 s | distilled_spirits | COINTREAU | LIQUEUR | 40.0 | Not read | 375 mL | Not read | FRANCE | Review needed |
| Cointreau_Back.jpg | 200 | 4.891 s | Not read | CONIT | Not read | Not read | Not read | Not read | MPORTED BY REMY COINTREAU USA INC. NEW YORK,NY | FRANCE | Review needed |
| coTpD.jpg | 200 | 4.275 s | wine | SUMMER BLUSH | PROVENCE-STYLE ROSE | 12.5 | Not read | 750 mL | PRODUCEOS BOTTLEDBY SUMMER BLUSK WINES.PASO ROBLES.CA | United States | Review needed |
| DDqT2.jpg | 200 | 5.020 s | distilled_spirits | NORTH LIGHT | DISTILLED VODKA | 40.0 | 80.0 | 750 mL | Not read | Not read | Review needed |
| DmK94.jpg | 200 | 3.931 s | wine | FROST RIDGE | Marlborough Sauvignon Blanc | 12.0 | Not read | 750 mL | Imported by Fros Ridge lparts Stattie, Washingion | New Zealand | Review needed |
| EqTB7.jpg | 200 | 4.289 s | distilled_spirits | SMOKE& AGAVE | Not read | 45.0 | 90.0 | 750 mL | Imoported by Smoke & Agave Imports, Los Angeles, California | Mexico | Review needed |
| Gemini_Generated_Image_auilqqauilqqauil (1).jpg | 200 | 4.733 s | distilled_spirits | SECRET | London Dry Gin | 47.0 | 94.0 | 1 L | Not read | Not read | Review needed |
| GuCzO.jpg | 200 | 4.225 s | distilled_spirits | FERRY | GOLDEN RUM | 40.0 | 80.0 | 750 mL | Imported by Old Ferry Spiris, Miami, Flonid Product of Barbados | Barbados | Review needed |
| iFZ0Q.jpg | 200 | 4.119 s | distilled_spirits | BLACKBIRD RESERVE | Kentucky Straight Bourbon Whiskey | 45.0 | 90.0 | 750 mL | Disilled and botted by Blackbird Dsuilling Co. Frankfort, Kentucky | Not read | Review needed |
| J3YuX.jpg | 200 | 3.015 s | malt_beverage | IRON ANCHOR BREWING CO. | INDIA PALE ALE | 7.2 | Not read | 16 fl oz | BREWED AND BOTTLED BY IRON ANCHOR BREWING CO. PORTLAND, MAINE | Not read | Review needed |
| JackDaniels_Back.jpg | 200 | 4.193 s | distilled_spirits | HPATNELS | Not read | Not read | Not read | Not read | DISTILLED AND BOTTLED BY JACK DANIEL DISTILLERY LYNCHBURG,TENNESSEE,USA | Not read | Review needed |
| JackDaniels_Front.jpg | 200 | 3.126 s | distilled_spirits | JACK DANIEL'S | WHISKEY | 40.0 | 80.0 | 375 mL | Not read | Not read | Review needed |
| jsP3W.jpg | 200 | 2.733 s | malt_beverage | MIDNIGHT FORGE | Imperial Oatmeal Stout | 9.5 | Not read | 12 fl oz | Brewed and bottled by Midnight Forge Brewing, Milwaukee, Wisconsin | Not read | Review needed |
| leTeL.jpg | 200 | 4.485 s | wine | IRON CREEK | Pinot Noir | 13.8 | Not read | 750 mL | PRODUCED AND BOTTLED BY IRON CREEK CELLARS | Not read | Review needed |
| MXteB.jpg | 200 | 2.490 s | malt_beverage | SUNDOCK | AMERICAN WHEAT ALE | 5.0 | Not read | 16 fl oz | Brewed and canned by Sun Dock Brewing. San Diego, California | Not read | Review needed |
| O0P0Z.jpg | 200 | 4.442 s | wine | CEDAR BEND | Chardonnay | 13.5 | Not read | 750 mL | Produced and bottled by Cedar Bend Vineyards Oregon. | Not read | Review needed |
| PtNj9.jpg | 200 | 2.569 s | distilled_spirits | BOTANIST'S SECRET | -London Dry Gin | 47.0 | 94.0 | 1 L | Distilled& bottled by Botanist's Secret Distillery, London. B Dy.ondon | Not read | Review needed |
| RevolverBrewing.jpg | 200 | 0.217 s | malt_beverage | REVOLVER | TEXAS STYLE ALE | Not read | Not read | Not read | REVOLVER BREWING LITTLETON, CO | Not read | Review needed |
| RevolverBrewing.png | 200 | 5.361 s | malt_beverage | REVOLVER | TEXAS STYLE ALE | Not read | Not read | Not read | REVOLVER BREWING LITTLETON, CO | Not read | Review needed |
| RevolverBrewing_2.jpg | 200 | 2.900 s | Not read | INGREDIENTS | Not read | 7.0 | Not read | 12 fl oz | Not read | Not read | Review needed |
| Test_TTB_Image_0001.jpg | 200 | 3.307 s | wine | STONE'S THROW | Valley Cabernet Sauvignon | 14.5 | Not read | 750 mL | Produced and bottled by Stone's Throw Vineyards, Napa, California | Not read | Review needed |
| Test_TTB_Image_0002.jpg | 200 | 2.805 s | distilled_spirits | NORTHWIND | VODKA | 40.0 | 80.0 | 750 mL | Distilled and bottled by Northwind. Spirits, Portland, Oregon | Not read | Differences detected |
| Test_TTB_Image_0003.jpg | 200 | 4.104 s | distilled_spirits | RED MESA | REPOSADO TEQUILA | 38.0 | 76.0 | 750 mL | Imported by Red Mesa Imports, San Antonio, Texas Hecho en Mexico | Mexico | Differences detected |
| Test_TTB_Image_0004.jpg | 200 | 3.459 s | distilled_spirits | CRYSTAL TUNDRA | Distilled Vodka | 40.0 | 80.0 | 1.75 L | Distilled and bottled by Crystal Tundra Spirits, Anchorage, Alaska | Not read | Review needed |
| Test_TTB_Image_0005.jpg | 200 | 3.083 s | distilled_spirits | BOTANIST'S SECRET | LONDON DRY GIN | 47.0 | 94.0 | 1 L | Distilled & bottled by. Botanist's Secret Distillery, London. | Not read | Review needed |
| Test_TTB_Image_0006.jpg | 200 | 2.021 s | distilled_spirits | BOTANIST'S SECRET | LONDON DRY GIN | 47.0 | 94.0 | 1 L | Distilled & bottled by. Botanist's Secret Distillery, London. | Not read | Review needed |
| Test_TTB_Image_0007.jpg | 200 | 2.876 s | malt_beverage | IGHT FORGE | IMPERIAL OATMEAL STOUT | 9.5 | Not read | 12 fl oz | Brewed and bottled by Midnight Forge Brewing. Milwaukee, Wisconsin | Not read | Review needed |
| Test_TTB_Image_0008.jpg | 200 | 2.860 s | wine | FROST RIDGE | Marlborough Sauvignon Blanc | 12.0 | Not read | 750 mL | Imported by Fros Ridge lparts Stattie, Washingion | New Zealand | Review needed |
| Test_TTB_Image_0009.jpg | 200 | 2.624 s | malt_beverage | IRON ANCHOR BREWING CO. | INDIA PALE ALE | 7.2 | Not read | 16 fl oz | Brewed and bottled by Iron Anchor Brewing Co., Portland, Maine. | Not read | Review needed |
| Test_TTB_Image_0011.jpg | 200 | 0.191 s | distilled_spirits | SECRET | London Dry Gin | 47.0 | 94.0 | 1 L | Not read | Not read | Review needed |
| Test_TTB_Image_0021.jpg | 200 | 3.241 s | distilled_spirits | BLACKBIRD RESERVE | KENTUCKY STRAIGHT BOURBON WHISKEY | 45.0 | 90.0 | 750 mL | Distilled & bottled by Blackbird Distilling Co., Bardstown, Kentucky | Not read | Review needed |
| Test_TTB_Image_0022.jpg | 200 | 2.298 s | distilled_spirits | BLACKBIRD RESERVE | KENTUCKY STRAIGHT BOURBON WHISKEY | 45.0 | 90.0 | 750 mL | Distilled & bottled by Blackbird Distilling Co., Bardstown, Kentucky | Not read | Review needed |
| Test_TTB_Image_0023.jpg | 200 | 3.887 s | wine | MARITIME | SPARKLING WINE | 12.5 | Not read | 750 mL | Produced and bottled by Maritime Cellars, Mendocino, California FRONT/BRAND LABEL | Not read | Review needed |
| Test_TTB_Image_0024.jpg | 200 | 2.984 s | wine | FROST RIDGE | MARLBOROUGH SAUVIGNON BLANC | 12.0 | Not read | 750 mL | Imported by Frost Ridge Imports, Seattle, Washington. | New Zealand | Review needed |
| Test_TTB_Image_0025.jpg | 200 | 2.745 s | distilled_spirits | BLACKBIRD RESERVE | Kentucky Straight Bourbon Whiskey | 45.0 | 90.0 | 750 mL | Disilled and botted by Blackbird Dsuilling Co. Frankfort, Kentucky | Not read | Review needed |
| Test_TTB_Image_0026.jpg | 200 | 1.860 s | malt_beverage | IRON ANCHOR BREWING CO. | INDIA PALE ALE | 7.2 | Not read | 16 fl oz | BREWED AND BOTTLED BY IRON ANCHOR BREWING CO. PORTLAND, MAINE | Not read | Review needed |
| Test_TTB_Image_0027.jpg | 200 | 3.053 s | distilled_spirits | CLEARWATER | BLANCO TEQUILA | 40.0 | 80.0 | 750 mL | Imported by Clearwater Spirits, Austin, Texas Hecho en Mexico. | Mexico | No differences found in checked fields |
| Test_TTB_Image_0028.jpg | 200 | 1.964 s | malt_beverage | MIDNIGHT FORGE | Imperial Oatmeal Stout | 9.5 | Not read | 12 fl oz | Brewed and bottled by Midnight Forge Brewing, Milwaukee, Wisconsin | Not read | Review needed |
| Test_TTB_Image_0029.jpg | 200 | 3.936 s | wine | FOX HOLLOW | RIESLING | 12.0 | Not read | 750 mL | Produced and bottled by Fox Hollow Vineyards, Hammondsport, New York | Not read | Review needed |
| Test_TTB_Image_0030.jpg | 200 | 3.117 s | wine | CEDAR BEND | Chardonnay | 13.5 | Not read | 750 mL | Produced and bottled by Cedar Bend Vineyards Oregon. | Not read | Review needed |
| Test_TTB_Image_0031.jpg | 200 | 2.929 s | malt_beverage | HARBOR LIGHTSE | PALE ALE | 5.2 | Not read | 12 fl oz | Brewed and bottled by Harbor Lights. Brewing Co., Seattle, Washington | Not read | No differences found in checked fields |
| Test_TTB_Image_0032.jpg | 200 | 1.984 s | distilled_spirits | BOTANIST'S SECRET | -London Dry Gin | 47.0 | 94.0 | 1 L | Distilled& bottled by Botanist's Secret Distillery, London. B Dy.ondon | Not read | Review needed |
| Test_TTB_Image_0033.jpg | 200 | 4.036 s | wine | LARK & LUMEN o:bsxdticbug= | ROSE | 13.0 | Not read | 750 mL | Produced and bottled by Lark &Lumen Winery, Sonoma, California | Not read | Review needed |
| Test_TTB_Image_0034.jpg | 200 | 2.943 s | wine | IRON CREEK | WILLAMETTE VALLEY PINOT NOIR | 13.8 | Not read | 750 mL | Produced and bottled by Iron Creek Cellars, McMinnville, Oregon | Not read | Review needed |
| Test_TTB_Image_0035.jpg | 200 | 3.646 s | wine | WHISPERING PINES ESTATE | CALIFORNIA CABERNET SAUVIGNON | 13.5 | Not read | 750 mL | Produced and bottled by Whispering Pines Estate, Napa, California. | Not read | Review needed |
| Test_TTB_Image_0036.jpg | 200 | 4.423 s | distilled_spirits | CASA DE LUNA | REPOSADO TEQUILA | 40.0 | 80.0 | 750 mL | Imported by Casa de Luna Spirits, Houston, Texas Hecho en Mexico | Mexico | No differences found in checked fields |
| Test_TTB_Image_0037.jpg | 200 | 3.111 s | distilled_spirits | BOTANIST'S SECRET | . LONDON DRY GIN - | 47.0 | 94.0 | 1 L | Distilled & bottled by Botanist's Secret Distillery, London | Not read | Review needed |
| Test_TTB_Image_0038.jpg | 200 | 3.239 s | malt_beverage | HARBORLIGHTS | Pale Ale | 5.2 | Not read | 12 fl oz | Not read | Not read | Review needed |
| Test_TTB_Image_0039.jpg | 200 | 4.882 s | wine | WHISPERING PINES -ESTATE | California Cabernet Sauvignon | 13.5 | Not read | 750 mL | Not read | Not read | Review needed |
| Test_TTB_Image_0040.jpg | 200 | 2.671 s | distilled_spirits | CASA DE LUNA | 100% Blue Agave Reposado Tequila | 40.0 | 80.0 | 750 mL | Imported by Casa de Luna Spirits, Housto Txs Hecho en Mexico | Mexico | Review needed |
| Test_TTB_Image_0041.jpg | 200 | 3.540 s | distilled_spirits | CRYSTAL TUNDRA | DISTILLED VODKA | 40.0 | 80.0 | 1.75 L | Distilled and bottled by Crystal Tundra Spirits, Anchorage, Alaska | Not read | No differences found in checked fields |
| Test_TTB_Image_0042.jpg | 200 | 3.984 s | distilled_spirits | OLD FERRY | AGED RUM | 40.0 | 80.0 | 1 L | Distilled and bottled by Old Ferry Rum Co., Charleston, South Carolina | Not read | Differences detected |
| uqgyU.jpg | 200 | 2.805 s | malt_beverage | HARBOR LIGHTS | Pale Ale | 5.2 | Not read | 12 fl oz | Not read | Not read | Review needed |
| Vodka_Back.jpg | 200 | 4.477 s | distilled_spirits | IN KULA.MAUI.HAWAI | 100%NEUTRAL SPIRITS DISTILLED | Not read | Not read | Not read | Not read | Not read | Review needed |
| Vodka_Front.jpg | 200 | 2.225 s | distilled_spirits | Not read | OrganicVodka | Not read | 80.0 | Not read | Not read | Not read | Review needed |
| wKE1J.jpg | 200 | 3.595 s | wine | WHISPERING PINES -ESTATE | California Cabernet Sauvignon | 13.5 | Not read | 750 mL | Not read | Not read | Review needed |
| XjPpA.jpg | 200 | 2.596 s | distilled_spirits | CASA DE LUNA | 100% Blue Agave Reposado Tequila | 40.0 | 80.0 | 750 mL | Imported by Casa de Luna Spirits, Housto Txs Hecho en Mexico | Mexico | Review needed |
| XXL_Back.jpg | 200 | 2.447 s | wine | OR MOREIN | GRAPE WINE WITH NATURAL FLAVORS | 16.0 | Not read | 750 mL | Not read | Not read | Review needed |
| XXL_Front.jpg | 200 | 3.425 s | Not read | STRAWBERRY | Not read | 16.0 | Not read | Not read | Not read | Not read | Review needed |
