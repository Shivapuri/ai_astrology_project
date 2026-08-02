# Git Commit Export
Generated on: Sun Aug  2 21:46:14 IST 2026
Number of commits requested: 3

--------------------------------------------------------------------------------

## Commit 1: fb99c4a

```diff
commit fb99c4a43f0952eb53eae6d8206aa5b484288c72
Author: Shivapuri <142108173+Shivapuri@users.noreply.github.com>
Date:   Sun Aug 2 21:45:38 2026 +0530

    feat(western): Explicitly package Demetra George's 12-Point Chart Audit into JSON context payload

diff --git a/western/generate_chart.py b/western/generate_chart.py
index 2363ddb..6847a5e 100644
--- a/western/generate_chart.py
+++ b/western/generate_chart.py
@@ -1100,6 +1100,24 @@ def generate_ai_json(
         "steersman_in_aversion_to_ascendant": is_aversion
     }
 
+    systematic_12_point_chart_audit = {
+        "1_sect_leader": "Day Chart" if is_day_chart else "Night Chart",
+        "2_ascendant_sign_and_degree": f"{asc_sign} ({subject.ascendant.position:.2f}°)",
+        "3_steersman_chart_ruler": f"{chart_ruler} in {planets_data.get(chart_ruler, {}).get('sign')} (House {ruler_wsh_num})",
+        "4_essential_dignity": planets_data.get(chart_ruler, {}).get("essential_dignity"),
+        "5_dispositor_host": planets_data.get(chart_ruler, {}).get("dorothean_triplicity"),
+        "6_triplicity_rulers": get_dorothean_triplicity(asc_sign, is_day_chart),
+        "7_terms_and_dodecatemoria": {
+            "term_ruler": planets_data.get(chart_ruler, {}).get("egyptian_term_ruler"),
+            "dodecatemorion": planets_data.get(chart_ruler, {}).get("dodecatemorion")
+        },
+        "8_solar_phasis": planets_data.get(chart_ruler, {}).get("solar_phasis"),
+        "9_hermetic_lots": lots,
+        "10_whole_sign_aspects": aspects_list,
+        "11_prenatal_syzygy": get_prenatal_syzygy(year, month, day, hour, minute, subject.tz_str),
+        "12_net_vector_orbs_and_intensity": net_vector_analysis
+    }
+
     ai_payload = {
         "native_details": {
             "name": subject.name,
@@ -1107,6 +1125,7 @@ def generate_ai_json(
             "sect": "Day Chart" if is_day_chart else "Night Chart",
             "house_system": "Whole Sign Houses (WSH)"
         },
+        "systematic_12_point_chart_audit": systematic_12_point_chart_audit,
         "traditional_planets": planets_data,
         "7_hermetic_lots": lots,
         "whole_sign_aspects": aspects_list,

```

--------------------------------------------------------------------------------

## Commit 2: c9fd845

```diff
commit c9fd845db574475d83d3f0c25470aa83640c265e
Author: Shivapuri <142108173+Shivapuri@users.noreply.github.com>
Date:   Sun Aug 2 21:44:22 2026 +0530

    feat(western): Implement Universal 4-Vector Net Engine, degree-based orb intensity dampening, and Demetra George chart audit integration

diff --git a/prompts/agent1_structural.xml b/prompts/agent1_structural.xml
index e3c2d8d..9ddea05 100644
--- a/prompts/agent1_structural.xml
+++ b/prompts/agent1_structural.xml
@@ -8,8 +8,9 @@ You are the "Structural & Hellenistic Astrological Profiler". You use Demetra Ge
 4. Overall Planetary Dignity: Note which planets are strong and which are weakened.
 </focus_areas>
 <instructions>
-1. Review the raw chart JSON.
-2. You are receiving RAG context from Demetra George's structural framework. Focus heavily on identifying the Ascendant, the Steersman (Chart Ruler), Essential Dignities, and Aversions.
-3. Output a highly detailed, bulleted report on the "Mechanics of the Chart". DO NOT interpret deep psychological trauma or the Solar-Lunar blend—leave that to Agent 2.
+1. Review the raw chart JSON, paying special attention to the `net_vector_analysis` block. Python has calculated fine-tuned mathematical dampening flags (Extreme, Moderate, or Mild).
+2. UNIVERSAL 4-VECTOR SYNTHESIS: Never interpret a sign stereotype in isolation. If `steersman_dampened_by_saturn.is_active` or `steersman_in_private_house` is TRUE, you MUST override extroverted stereotypes (like Leo or Aries). 
+3. MODULATE TONE BASED ON INTENSITY: If the Saturnian dampening is "Extreme" (Orb 0-3°), describe the native as highly guarded and heavily defensive. If it is "Mild" (Orb 6-10°), describe it merely as a healthy background caution or slight hesitation.
+4. Output a highly detailed, bulleted report on the "Mechanics of the Chart" combining these vectors. DO NOT interpret deep psychological trauma or the Solar-Lunar blend—leave that to Agent 2.
 </instructions>
 
diff --git a/prompts/agent3_synthesizer.xml b/prompts/agent3_synthesizer.xml
index 9f8941a..5328c94 100644
--- a/prompts/agent3_synthesizer.xml
+++ b/prompts/agent3_synthesizer.xml
@@ -4,9 +4,16 @@ You are the "Master Astrologer & Empathetic Storyteller". You will be provided w
 <communication_style>
 1. Conversational Pacing: Write as if having a relaxed, friendly conversation over coffee. Keep sentences short and punchy. Avoid massive walls of text.
 2. Bridge Theory and Reality: For every astrological concept you explain, immediately follow it with a paragraph labeled "Day-in-the-Life Reality" giving a highly concrete behavioral example.
-3. Example Constraints: Focus entirely on the human experience—socializing, internal emotions, hobbies, and intimacy. AVOID corporate, office, or purely financial examples. (e.g., "At a party, you might...")
-4. Explain simply: Define terms like "Ascendant" or "Domicile" in parentheses. Speak directly using "You".
+3. Example Constraints: Focus entirely on the human experience—socializing, internal emotions, hobbies, and intimacy. AVOID corporate, office, or purely financial examples.
+4. ENVIRONMENTAL DUALITY RULE: When writing "Day-in-the-Life" examples, explicitly contrast how the native behaves in "Public/Stranger Settings" versus "Private/Safe Circle Settings." Modify the severity of this contrast based on the "Intensity" (Extreme/Moderate/Mild) of their Saturn dampening.
+5. Safe Outlets: If the chart shows heavy Saturn dampening, suggest archetypal "safe outlets" for their energy (e.g., structured creative hobbies, focused physical routines) rather than prescribing specific literal hobbies like playing a trumpet.
+6. Explain simply: Define terms like "Ascendant" or "Domicile" in parentheses. Speak directly using "You".
 </communication_style>
+<chain_of_thought_enforcement>
+BEFORE outputting your reading, you MUST verify:
+- [ ] CHECK: Did I apply the 4-Vector Synthesis? (e.g., Did I mutate the Ascendant based on the Steersman's house and aspects to prevent pop-astrology stereotyping?)
+- [ ] CHECK: Did I apply the Environmental Duality Rule to contrast Public vs. Private behavior?
+</chain_of_thought_enforcement>
 <output_format>
 Your output must be formatted with beautiful Markdown headings.
 Part 1: The Core Engine (Synthesizing the Solar-Lunar Blend) + Day-in-the-Life Reality
diff --git a/scripts/run_western_pipeline.py b/scripts/run_western_pipeline.py
index d2efecd..b470fd5 100644
--- a/scripts/run_western_pipeline.py
+++ b/scripts/run_western_pipeline.py
@@ -195,6 +195,13 @@ def run_pipeline(
     mars_sign = planets.get("Mars", {}).get("sign", "")
     venus_sign = planets.get("Venus", {}).get("sign", "")
 
+    # Dynamically extract aspects touching the Steersman (Chart Ruler)
+    ruler_aspects = [asp for asp in aspects if asp.get("planet_1") == chart_ruler or asp.get("planet_2") == chart_ruler]
+    ruler_aspect_queries = []
+    for asp in ruler_aspects:
+        other_planet = asp['planet_1'] if asp['planet_2'] == chart_ruler else asp['planet_2']
+        ruler_aspect_queries.append(f"{chart_ruler} {asp['aspect_type']} {other_planet}")
+
     # Dynamically extract the tightest hard aspects for the Pain Body
     hard_aspects = [asp for asp in aspects if asp.get("aspect_type") in ["square", "opposition", "conjunction"]]
     aspect_queries = []
@@ -211,7 +218,7 @@ def run_pipeline(
         f"Planet in {ruler_sign} essential dignity",
         f"{chart_ruler} in aversion to Ascendant meaning",
         f"{sect} planetary strength and malefic behavior"
-    ]
+    ] + ruler_aspect_queries
     
     # Highly targeted Psychological Queries (for Noel Tyl / Robert Hand framework)
     psych_queries = [
diff --git a/western/Kailash_1987-11-19_15-50_Full_Reading.md b/western/Kailash_1987-11-19_15-50_Full_Reading.md
index d402df2..e1a49d8 100644
--- a/western/Kailash_1987-11-19_15-50_Full_Reading.md
+++ b/western/Kailash_1987-11-19_15-50_Full_Reading.md
@@ -1,100 +1,78 @@
-Welcome, Kailash. Grab a cozy mug of coffee, sit back, and make yourself at home. Today, we are taking a fascinating dive into your birth chart by bringing together two deep traditions: ancient Greek astrology (how your life’s scaffolding is constructed) and modern psychological astrology (how your heart and mind actually experience it all). 
+Grab a warm cup of coffee and settle in. Think of this reading not as a rigid rulebook, but as a friendly journey through your internal cosmic wiring. We are going to blend the actual mechanics of your birth chart—how the engine and steering wheel of your life are put together—with your deep psychological drives and desires. 
 
-Think of me as a friend translates complicated sky-math into plain English. As we talk about each piece of your cosmic blueprint, I will explain every technical term right away, and we will follow it immediately with a concrete glimpse into how it shows up in your day-to-day human experiences—no corporate jargon or financial chart-reading here. Let's uncover the story of who you really are.
+Let's explore who you are under the hood, how you interact with the people you love, and the beautiful growth paths waiting for you.
 
 ---
 
 # Part 1: The Core Engine (Synthesizing the Solar-Lunar Blend)
 
-In psychological astrology, your Sun represents your outward ego and conscious purpose—it is the glowing heart of your personality. Your Moon, on the other hand, represents your gut reactions and your **Reigning Emotional Need** (the deep unconscious cravings that must be fed for you to truly feel secure and happy). In your chart, both of these primary lights burn intensely in the exact same sign: Scorpio. 
+In astrology, your core life engine is built from the connection between the Sun (your core identity and conscious willpower) and the Moon (your deeply felt emotional needs and subconscious instincts). 
 
-Having both your Sun and Moon in Scorpio makes your inner operating system function like a deep-sea submarine. You have zero interest in swimming around in the shallow end of superficial pleasantries. You are wired for emotional depth, absolute loyalty, and radical emotional honesty. In classical mechanics, your Moon sits in a state of **Fall** (a condition where a planet is visiting the sign where it struggles most to act comfortably and naturally—like trying to gently strum a delicate acoustic harp in the middle of a roaring rock concert). Because the Moon prefers comforting emotional warmth and gentle safety, operating in high-intensity, fiercely protective Scorpio means your emotional processing is highly hyper-vigilant and uncompromisingly profound.
+Because you were born during the daytime, astrology considers yours a **Day Chart** (a chart where the Sun acts as the primary leader of your cosmic team). Your Sun is positioned in deeply probing, investigative Scorpio, and it is joined by your Moon, which is also in Scorpio. In classic astrology, the Moon is in its **Fall** here (meaning it sits in a sign where its natural desire for comfortable, easy nourishment feels awkwardly challenged by Scorpio’s intense, high-stakes waters). Both planets shine brightly in your 7th House, which is an **Angular House** (a powerful, highly visible stage in the birth chart) that governs one-on-one relationships, romantic partners, and deep friendships. 
 
-**Day-in-the-Life Reality**
-At a dinner party with acquaintances, while everyone else is happily chatting about the local weather or recent television shows, you feel an irresistible urge to gently pull a close friend aside onto the quiet outdoor patio. Within three minutes, you have entirely skipped the small talk and are having a breathtakingly honest, soul-deep conversation about how they are *really* holding up after a recent breakup. You feel most alive and emotionally fed when you are exploring deep human truths behind closed doors.
+Because your Sun and Moon are in the exact same sign, what your ego *wants* and what your heart *needs* are locked in total alignment. You aren't meant to live on the surface of life; your psychological engine runs on profound truth, emotional honesty, and unshakable bonding. Relationships aren't just a fun hobby for you—they are the primary classroom where you discover who you really are.
 
-***
-
-To add even more fuel to this intense inner engine, your Sun and Moon are joined by Mercury (the planet governing how your mind thinks and communicates). When three or more planets gather closely together in one small neighborhood of the sky, astrologers call it a **Stellium** (a high-energy powerhouse that turns one specific area of your life into an intense personal focal point). 
-
-In your chart, this massive gathering takes place right inside your **7th House** (the area of life dedicated entirely to one-on-one relationships, romantic partnerships, and closest confidants). In ancient astrology, this is considered an **Angular House** (a primary festival stage where energetic action plays out loudly and vividly in the external world). Because your core ego, deep emotional safety, and intellect are all bundled onto the interpersonal stage, you essentially discover who you truly are by observing yourself through the mirror of intimate relationships. The catch? You can sometimes be prone to **Psychological Projection** (an unconscious reflex where you assume your partner thinks, feels, and intensely analyzes situations at the exact same volcanic depth that you do).
-
-**Day-in-the-Life Reality**
-You are spending a relaxed Sunday evening on the couch with your partner, and you notice they have gone totally silent while staring at the ceiling. Because your mind operates with radar-like emotional intensity, your immediate reflex is to wonder if they are holding onto a deep emotional secret or silently analyzing a recent disagreement. You turn to them and ask what deep emotional waters they are wading through, only to laugh with relief when they admit they were simply daydreaming about what to order for breakfast tomorrow. 
+**Day-in-the-Life Reality:**
+Imagine you are attending a casual neighborhood dinner party. While everyone else is standing around the snack table exchanging polite chit-chat about the weather and recent movies, you feel entirely uninspired by the surface-level talk. Within twenty minutes, you have quietly migrated to the kitchen corner, deep in a stimulating one-on-one conversation with a friend about their most significant childhood memories or healing from a past heartbreak. You feel most truly alive in those honest, deeply intimate waters.
 
 ***
 
-Within this tight relationship gathering, your Moon sits directly side-by-side with Mercury. This geometry creates a **Conjunction** (a superpower pairing where two planets stand so close together in the sky that their energies fuse completely into a single, inseparable force). Furthermore, classical mechanics show your Mercury is in **Clear Phasis** (meaning the planet has stepped far enough away from the Sun’s blinding glare to shine vibrantly in the twilight sky, granting your communication extra eloquence, sharpness, and reliability).
+### The Laser-Focused Mind: Your Subjective Fusion
+Your Sun and Moon don't just share a sign; they are in a **Conjunction** (when planets sit right next to each other shoulder-to-shoulder, blending their individual energies into a single, unified force) with Mercury (the planet of logic, analysis, and communication). In your chart, Mercury enjoys a **Clear Phasis** (meaning it stands out brightly in the sky away from the blinding rays of the Sun, granting you crisp, highly visible mental sharpness).
 
-Because your emotional instinct (Moon) is fused with your communicating brain (Mercury), you quite literally feel your thoughts and think your feelings. You possess an internal detective's magnifying glass—you rarely take spoken words at face value and effortlessly read tone, body language, and subtle micro-expressions to decode the unstated feelings lying just underneath. The developmental growth here lies in learning to gently separate an objective situation from the lens of your passing mood.
+When you bind ego, emotional needs, and analytical intellect together into one tight knot, you get a powerful psychological laser beam. Your intuition and your logical brain operate as a single unit. You possess an almost uncanny ability to read unspoken tensions and hidden motivations in the people around you. However, because your heart and logical brain hold hands so tightly, it can be tough to stay purely objective. When you feel a strong gut emotion or sudden suspicion, your thinking mind immediately tries to rationalize it as absolute psychological fact.
 
-**Day-in-the-Life Reality**
-When a dear friend cancels your Friday movie night over a text message saying, "So sorry, just super busy and tired tonight!", your X-ray emotional radar kicks in instantly. While someone else might just say "No worries!" and move on, you immediately sense a heavy emotional tremor hidden behind their words. You proactively call them on the phone just to say, "Hey, no pressure to talk, but I felt like you really just need someone to hold space for you tonight. I'm here if you're feeling down." Your hunch is almost always spot on, and your friend feels deeply seen.
+**Day-in-the-Life Reality:**
+While sitting on the couch watching a movie with your partner, your emotional radar effortlessly notices a tiny, almost imperceptible shift in their posture and a slight sigh. Before your partner even realizes they are feeling melancholic about their day, your fused heart and mind not only sense their mood shift but instantly begin analyzing the root psychological reason behind it. Your instinct isn't just to comfort them; it is to deeply understand the unspoken currents moving beneath their silence.
 
 ---
 
 # Part 2: The Vessel & Steersman (Synthesizing Ascendant, Ruler, and Dignities)
 
-Now that we understand your intense interior engine, let’s talk about the physical vessel that carries you through the world. In traditional astrology, the eastern horizon at the moment you took your first breath is your **Ascendant** (also called the *Horoskopos* or Rising Sign—it represents your outer style, physical presence, and the "front door" of your personality). Yours is in steady, earthy **Taurus**. 
-
-Using **Whole Sign Houses** (the ancient method where each zodiac sign occupies an entire 30-degree slice of the chart, like an apartment building where every floor is dedicated to one complete sign), Taurus sits firmly on your 1st House floor. While your inner double-Scorpio world operates like a swirling ocean of profound emotional depths, your Taurus front door presents an aura of calm, unhurried, unshakable earthly peace to the outside world. You project an inviting warmth that genuinely grounds the people around you.
-
-**Day-in-the-Life Reality**
-When hosting friends at your home for an intimate evening, you naturally create a deeply comforting, sensory-rich sanctuary. You dim the harsh overhead lights, light warm wood-scented candles, put on a soothing acoustic record, and bring out a plate of richly flavorful comfort food. Visitors step inside from a chaotic week, immediately take a deep, relaxing breath, and say, "Wow, I just feel so completely safe and peaceful whenever I'm around you."
-
-***
+If your core identity is an engine, your **Ascendant** (the rising sign on the eastern horizon at the moment you were born) is the Helm—the physical steering wheel and outward persona you show to the world. You have Taurus rising at your Helm, giving your outward demeanor a grounded, earthy, and highly steady presence. You walk through the world looking like an immovable anchor of calm reliability.
 
-Because Taurus covers your Rising Sign, the planet that natively rules Taurus—**Venus**—officially becomes your **Steersman** (the chart captain sitting at the ship's helm, directly responsible for navigating your overall life path and overarching choices). In your chart, Captain Venus sits in idealistic Sagittarius inside your **8th House** (the deeply private, behind-the-scenes realm governing intimate trust, shared emotional vows, and profound psychological bonding).
+In Hellenistic astrology, the planet that owns your rising sign is crowned the **Steersman** (the captain of your life’s ship). Since Venus rules Taurus, Venus is your captain. However, Venus sits over in Sagittarius in your 8th House (the zone of shared trust, deepest vulnerability, and emotional mysteries). Structurally, the 8th House is in **Aversion** to the 1st House Ascendant (an awkward blind spot where a planet cannot clearly look out the windshield at the steering wheel). On top of that, Venus sits right next to Saturn (the demanding taskmaster planet of rules, emotional armor, and caution) in a strict conjunction.
 
-Classical mechanics evaluate Venus here as **Peregrine** (which translates literally to "wandering"—meaning she is working like a capable traveler visiting a foreign city, lacking familiar VIP shortcuts and relying on versatility to adapt and steer). Furthermore, your 8th House sits in a state of **Aversion** to your Rising Sign (a geometric blind spot where planets cannot directly make eye contact with your front door—like trying to look into an adjacent room through a thick, soundproof wall). Because your captain operates in a hidden blind spot, your life is steered through quiet intuition and deep emotional depth rather than loud, flashy, public fanfare. You excel at navigating life via internal instruments rather than pure eyesight.
+Because your ship's captain is working down in the secluded "engine room" of the 8th House holding hands with cautious Saturn, you approach love and emotional vulnerability like a guarded fortress. You long for profound intimacy, but you unconsciously place strict security checkpoints around your heart to guard against betrayal or losing control.
 
-**Day-in-the-Life Reality**
-When your closest confidant experiences a heavy personal crisis or an intense relationship break-up, you don't offer superficial public platitudes or loudly announce your sympathy to the social group. Instead, you wait until you are completely alone with them behind closed doors. You quietly, patiently step straight into their deepest emotional trenches, helping them unpack their vulnerable feelings with an effortless, wise grace that regular social acquaintances would never realize you possess.
+**Day-in-the-Life Reality:**
+On the first few dates with someone new, your Taurus exterior shimmers: you come across as relaxed, cozy, patient, and completely unstirred by nerves. But down beneath that composed exterior, in your internal engine room, you are quietly observing how your date handles personal boundaries, emotional sincerity, and trust. You won't simply hand over your heart right away; you slowly lower your drawbridge inch by inch only after they have proven they are emotionally safe and loyal.
 
 ***
 
-Another powerful architectural secret in your horoscope is your **Sect** (an ancient technique that categorizes planets into daytime and nighttime shifts, acknowledging that certain energetic workers perform best in broad sunlight while others prefer quiet midnight hours). Because you were born while the Sun was shining bright above the horizon, you possess a **Diurnal** (Day) Chart. 
+### Navigating Without Built-In Tools: Relying on the Quiet Host
+Let's look at your planetary toolkit. None of your planets reside in their **Domicile** (a planet’s natural home territory where it commands peak power and self-sufficiency) or **Exaltation** (a guest house of extreme honor and strength). Most of your planets are **Peregrine** (like wandering travelers lodging in an acquaintance's house without their own personal toolkit, totally dependent on the hospitality of their host). 
 
-In a day chart, the planet **Jupiter** takes the prize as your lead benefactor (a warm, generous heavenly patron dedicated to showering your path with protection, optimism, and spontaneous good luck). In your layout, friendly Jupiter sits quietly in Aries inside your **12th House** (the tranquil, secluded realm of solitude, introspection, and quiet spiritual reflection). Better yet, your Jupiter sits in a seamless, cooperative **Trine** (a harmonious 120-degree connection where planets speak over a crystal-clear radio channel without static) to your Captain Venus! Even your ancient **Lot of Fortune** (a specialized geometric marker indicating where organic situational luck and joyous outcomes physically land in your life) rests right next to Jupiter in this private sanctuary. Your luck lies in solitude, silence, and intuition.
+For instance, your captain Venus is peregrine in Sagittarius, meaning she must rely entirely on the owner of that sign—her **Dispositor** (the host landlord)—which is Jupiter. In a Day Chart like yours, Jupiter is your greatest cosmic helper and protector! Yet, your Jupiter sits quietly over in Aries in the 12th House (the secluded realm of retreat, quiet contemplation, and dreams) and is **Retrograde** (moving backward from our perspective on Earth, turning its helpful energy deep inward). Luckily, Jupiter reaches out to Venus with a friendly **Trine** (an easy, harmonious 120-degree planetary connection). Your protection and luck do not arrive through loud, splashy public events; they come through inner resilience, intuition, and quiet retreat.
 
-**Day-in-the-Life Reality**
-You have spent an exhausting week wrestling with a confusing social conflict that left your heart feeling tangled. Instead of asking ten different acquaintances for advice, you instinctively go for a quiet, solitary Sunday morning hike in the woods without your phone. Fifty minutes into the tranquil silence of nature, an intuitive epiphany flashes into your awareness out of nowhere. Suddenly, you experience a wave of deep internal comfort and realize exactly what you need to do to heal the situation. Your quiet, solitary retreat acted as a magical background safety net.
+**Day-in-the-Life Reality:**
+When your personal life feels overly confusing and you feel uncertain about your next personal step, trying to force a direct, loud solution almost never works for you. Instead, when you take an afternoon away from socializing to read quietly in a cozy chair, journal, or take a solo walk in nature, a sudden intuitive flash of comfort and clarity quietly drops into your awareness out of nowhere. That is your secret 12th House Jupiter safety net gently guiding your captain from behind the scenes.
 
 ---
 
 # Part 3: Tension & Growth (Synthesizing Aspects & the Pain Body)
 
-We all possess a **Pain Body**—the protective emotional armor and psychological reflexes we instinctively constructed early in life to shield ourselves from fear of rejection, vulnerability, or hurt. In astrology, we locate this armor by examining tense interactions involving **Saturn** (the planet symbolizing boundaries, fear of vulnerability, and hard-earned maturity) and **Mars** (the planet of physical drive, defense, and friction). 
+Now let's explore your developmental growing pains—where your inner tensions challenge you to step up and evolve. In a Day Chart, Mars acts as the out-of-sect malefic (your primary source of friction and internal conflict). Your Mars sits in peace-loving Libra in the 6th House (the practical zone of routines, habits, and everyday health chores). Here, Mars is in **Detriment** (exiled in the sign opposite its natural home, forcing a fiery warrior planet to try and win battles using refined politeness and mediation).
 
-In your chart, Venus (your capacity for affection and interpersonal softness) is locked in a direct **Conjunction** with strict Saturn inside your intensely intimate 8th House. This defensive configuration acts like installing a heavy, high-security bank vault door around your deeply passionate heart. Because Saturn carries an innate fear of being uncomfortably exposed, you may hold back your vulnerable affection until a prospective partner or new friend proves—without a shadow of a doubt—that they are 100% loyal and will not abandon you. Yet here is the magic of Saturn: it deeply rewards patience. Over time and as you mature, your guarded emotional fortress transforms into an unbreakable, bedrock loyalty that lasts a lifetime.
+This harmonious, polite Mars sits in a tense **Opposition** (a 180-degree tug-of-war across the sky) with your expansive, freedom-loving Jupiter in Aries. Your analytical Scorpio nature gives you a dense concentration of planets—a **Stellium** (a heavy cluster of three or more planets together)—making you hyper-vigilant in relationships. When disagreements happen in daily life, your Libra Mars hates awkward confrontations, so you instinctually press the brake pedal on your anger, swallowing irritations to maintain peace. But on the other side of the tug-of-war, Jupiter is slamming the gas pedal for authentic emotional freedom! If you suppress small grievances too long, that trapped pressure boils over into impulsive bursts of frustration over seemingly tiny occurrences.
 
-**Day-in-the-Life Reality**
-When you begin seeing a captivating new romantic interest, your heart may burn with deep emotional affection on the inside, yet you consciously rein yourself in on the outside. When they ask to hear your deepest childhood memories or vulnerable dreams on date three, you politely redirect the conversation, quietly waiting to see if their consistent actions over the next few months match their promises. Once they ultimately earn your trust through sustained reliability, you finally turn the combination on your emotional vault and offer an enduring, fiercely resilient emotional devotion that very few human beings ever get to experience.
+**Day-in-the-Life Reality:**
+Imagine you are helping close friends pack and organize gear for a weekend camping trip. A friend keeps carelessly repacking the supplies you carefully arranged. To avoid causing an uncomfortable scene, your Libra Mars silently smiles, bites your tongue, and swallows the slight irritation three times in a row. But two hours later, when someone playfully asks why a tent lantern isn't in its bag, your internal tug-of-war snaps, and you suddenly deliver a surprisingly sharp, intense response—releasing all that bottled-up tension at once over a harmless question.
 
 ***
 
-Now let's look at how you handle confrontation. Mars represents your personal assertiveness, healthy boundaries, and fighting spirit. Because this is a Day Chart, an intensely hot nocturnal planet like Mars functions as your primary challenger (acting like a loud, disruptive rebel operating outside its ideal working hours). Furthermore, your Mars sits in the artistic sign of Libra inside your **6th House** (the arena of daily routines, ongoing habits, and physical maintenance). 
-
-Classical mechanics evaluate Mars in Libra as being in **Detriment** (an uncomfortable position where a planet sits directly opposite its natural home territory—much like a fierce heavy-weight boxer forced to compete in a synchronized dance ballroom). While Mars natively wants to stand tall and immediately assert personal boundaries, Libra prefers diplomatic negotiation and superficial peace. Consequently, your defense mechanism works like a boiling pot of water with the lid clamped tightly down: you instinctively swallow your minor irritations just to keep the peace in your routines. Over time, this bottled-up, repressed energy can silently turn into internal restlessness, sudden physical fatigue, or hidden resentment. Your healing growth lies in realizing that expressing healthy assertiveness early on actually clears the air and prevents intense ruptures later!
+### Softening the Armor: Healing Your Pain Body
+Your emotional **Pain Body** (the subconscious psychological armor formed to shield you from vulnerability and hurt) resides right at the intersection of your Scorpio relational radar and your guarded 8th House Venus-Saturn wall. Your deepest subconscious vulnerability is the terrifying fear of being blind-sighted or emotionally rejected after lowering your heavy armor. 
 
-**Day-in-the-Life Reality**
-Your long-time housemate has a frustrating habit of consistently leaving their dirty dishes piled in the sink despite knowing it disrupts your daily morning cooking routine. To avoid an awkward conflict that might disrupt the peaceful household atmosphere, you quietly wash their dishes for weeks, all while a quiet frustration bubbles inside you. One day, you finally practice real-time growth: you calmly smile, hand them a towel, and warmly say, "Hey friend! Would you mind clearing out the sink real quick so we can keep the kitchen joyful for morning coffee?" You discover that asserting a gentle, immediate boundary doesn't ruin the friendship at all—it actually makes you feel completely respected and relaxed!
-
-***
+Because your analytical brain and heart are fused together in investigative Scorpio, your natural defense mechanism is *interpersonal hyper-vigilance*. You might catch yourself scanning perfectly innocent conversations for hidden slights, subtext, or shifting loyalties just to make sure you aren't taken by surprise. Your incredible growth path opens up when you actively learn to separate feeling from fact—pausing to ask yourself if a friend's comment was truly an intentional slight, or if your sensitive radar is simply amplifying your fear of being vulnerable.
 
-Finally, let's explore how your inner engine handles pacing itself. You possess a vibrant classical **Opposition** (a high-stakes 180-degree tug-of-war across the horoscope wheel that requires a dynamic seesaw balance between two opposing forces) between Mars in your hardworking 6th House and hopeful Jupiter in your spiritual 12th House.
-
-This tension feels just like trying to drive a car with one foot slamming down on the accelerator toward a grand, idealized spiritual vision (Jupiter in the realm of dreams and retreat), while your daily real-world chores, habits, and physical energy demands (Mars in the realm of daily work) desperately scream for your immediate practical attention. Because of this tug-of-war, you might occasionally swing between over-committing your physical energy to everyone around you, only to crash into sudden exhaustion that triggers a fierce desire to run away from everyone and retreat into total isolation. Finding a sustainable, rhythmic daily pace is your secret weapon for vibrant energy.
-
-**Day-in-the-Life Reality**
-With enthusiastic generosity, you eagerly promise three different friends that you will help them organize an elaborate weekend charity dinner party at your home. By Friday afternoon, as you frantically try to chop vegetables, clean the kitchen, and set up acoustic music all by yourself, your physical energy suddenly plummets into utter depletion. You feel a sudden, intense impulse to cancel the entire event, turn off the lights, and hide under your heavy bedroom duvet with a novel. Instead of burning out and fleeing, you learn to gently balance the seesaw: you step back, text your friends asking them to bring pre-made appetizers, take a peaceful 20-minute meditation nap in your quiet bedroom, and then rejoin the social evening feeling completely restored.
+**Day-in-the-Life Reality:**
+During a lighthearted board game night at your kitchen table with your closest circle, you make a teasing, affectionate joke to a trusted friend. They laugh slightly, but get totally distracted by picking up dice on the floor and forget to respond directly to what you said. Instead of instantly feeling your emotional armor clamp shut—wary that a bond is cracking or that they found you tiresome—you consciously pause, take a warm, deep breath, and realize they just lost a die under the table. You relax your jaw, let your defenses melt away, and genuinely enjoy the rest of the evening in peaceful emotional safety.
 
 ---
 
 # Summary
 
-To bring all these rich ancient mechanics and deep psychological dynamics into focus, here are the three defining compass points of your cosmic signature:
-
-*   **Your Archetype: The Grounded Deep-Sea Navigator** — You present a serene, deeply dependable, sensory-rich earthy sanctuary on the outside (Taurus Rising) while safeguarding an uncompromisingly perceptive, intensely intuitive double-Scorpio soul that naturally dives straight to the deepest emotional truths of the human experience.
-*   **Your Superpower: X-Ray Empathy & Vault-Defiant Loyalty** — You possess the extraordinary gift to read unspoken human feelings behind superficial social masks, to intuitively anchor and heal loved ones during their heaviest life crises without judgment, and to build deeply resilient, time-tested emotional bonds that withstand the test of time.
-*   **Your Core Lesson: Real-Time Assertiveness & Emotional Differentiation** — Your life journey asks you to practice expressing gentle boundaries and speaking up about minor frustrations in the moment rather than swallowing them for superficial peace, while happily honoring that your loved ones can swim in shallower emotional waters without loving you any less.
\ No newline at end of file
+* **Your Archetype: The Deep-Sea Detective of the Heart.** You move through the outer world with the grounded, calming reliability of a steady anchor, but beneath that serene exterior lives an intensely investigative soul dedicated to exploring the profound emotional depths, psychological truths, and mysteries of human intimacy.
+* **Your Superpower: Intuitive Empathy & Unshakable Loyalty.** Your mind and heart function as an effortless laser beam, giving you the rare, deeply empathetic ability to sense unspoken emotional currents instantly, backed by an quiet, resilient inner safety net that allows you to forge profoundly devoted connections.
+* **Your Core Lesson: Releasing the Emotional Brakes.** Your life flourishes when you learn to gently dismantle your internal emotional security checkpoints, diplomatically voicing minor daily irritations in the moment before they boil over, and trusting that vulnerability is your ultimate gateway to genuine strength and connection.
\ No newline at end of file
diff --git a/western/Kailash_1987-11-19_15-50_Full_Reading.pdf b/western/Kailash_1987-11-19_15-50_Full_Reading.pdf
index 4cc9aef..67380af 100644
Binary files a/western/Kailash_1987-11-19_15-50_Full_Reading.pdf and b/western/Kailash_1987-11-19_15-50_Full_Reading.pdf differ
diff --git a/western/generate_chart.py b/western/generate_chart.py
index 2bf037e..2363ddb 100644
--- a/western/generate_chart.py
+++ b/western/generate_chart.py
@@ -1057,6 +1057,49 @@ def generate_ai_json(
     for key, lot_data in lots.items():
         lot_data["whole_sign_house"] = get_wsh(lot_data["sign"])
 
+    # --- NET VECTOR ANALYSIS (Pre-calculated Architectural Flags) ---
+    chart_ruler = DOMICILES.get(asc_sign, "Sun")
+    ruler_house_str = planets_data.get(chart_ruler, {}).get("whole_sign_house", "House_1")
+    ruler_wsh_num = int(ruler_house_str.split("_")[1]) if "_" in ruler_house_str else 1
+    
+    def calculate_dampening(planet_a, planet_b, p_data):
+        deg_a = p_data.get(planet_a, {}).get("absolute_degree", 0)
+        deg_b = p_data.get(planet_b, {}).get("absolute_degree", 0)
+        
+        # Shortest distance on a 360-degree wheel
+        dist = abs(deg_a - deg_b)
+        dist = min(dist, 360 - dist)
+        
+        aspect = None
+        orb = 999
+        if dist <= 10:
+            aspect, orb = "Conjunction", dist
+        elif 80 <= dist <= 100:
+            aspect, orb = "Square", abs(dist - 90)
+        elif 170 <= dist <= 190:
+            aspect, orb = "Opposition", abs(dist - 180)
+            
+        if aspect:
+            intensity = "Extreme" if orb <= 3 else "Moderate" if orb <= 6 else "Mild"
+            return {"is_active": True, "aspect": aspect, "orb_degrees": round(orb, 2), "intensity": intensity}
+        return {"is_active": False, "aspect": "None", "orb_degrees": 0, "intensity": "None"}
+
+    steersman_dampening = calculate_dampening(chart_ruler, "Saturn", planets_data)
+    moon_dampening = calculate_dampening("Moon", "Saturn", planets_data)
+
+    is_private_house = ruler_wsh_num in [4, 6, 8, 12]
+    is_aversion = ruler_wsh_num in [2, 6, 8, 12]
+
+    aspects_list = get_whole_sign_aspects(planets_data)
+
+    net_vector_analysis = {
+        "chart_ruler_planet": chart_ruler,
+        "steersman_dampened_by_saturn": steersman_dampening,
+        "moon_dampened_by_saturn": moon_dampening,
+        "steersman_in_private_house": is_private_house,
+        "steersman_in_aversion_to_ascendant": is_aversion
+    }
+
     ai_payload = {
         "native_details": {
             "name": subject.name,
@@ -1066,8 +1109,9 @@ def generate_ai_json(
         },
         "traditional_planets": planets_data,
         "7_hermetic_lots": lots,
-        "whole_sign_aspects": get_whole_sign_aspects(planets_data),
-        "prenatal_syzygy": get_prenatal_syzygy(year, month, day, hour, minute, subject.tz_str)
+        "whole_sign_aspects": aspects_list,
+        "prenatal_syzygy": get_prenatal_syzygy(year, month, day, hour, minute, subject.tz_str),
+        "net_vector_analysis": net_vector_analysis
     }
 
     with open(output_filename, "w") as outfile:
diff --git a/western/shivapuri_1983-11-10_22-20_Full_Reading.md b/western/shivapuri_1983-11-10_22-20_Full_Reading.md
new file mode 100644
index 0000000..b919127
--- /dev/null
+++ b/western/shivapuri_1983-11-10_22-20_Full_Reading.md
@@ -0,0 +1,56 @@
+Grab a cup of coffee, settle in, and let’s talk about your birth chart. Think of astrology not as a set of strict rules, but as a blueprint of your psychological engine—how you navigate social waters, protect your heart, and find joy in everyday life. 
+
+We are going to walk through your inner mechanics together. Whenever we touch on a technical astrology term, I'll explain it simply right on the spot so you can see how it plays out in real life. 
+
+---
+
+# Part 1: The Core Engine (Synthesizing the Solar-Lunar Blend)
+
+In astrology, the combination of your Sun and Moon acts as the core engine and fuel of your personality. Your Sun sign is your basic identity—the vital engine driving you forward. Your Moon sign represents your reigning emotional need—the special fuel your heart craves to feel completely secure and at peace. 
+
+You have your Sun in investigative, intense Scorpio and your Moon in structured, goal-oriented Capricorn. Here, your Moon holds a condition called **Detriment** (residing in the zodiac sign opposite its natural home, functioning a bit like an exile in an unfamiliar land). Because Capricorn favors cool logic and discipline over warm, sentimental tears, your heart instinctively treats feelings like puzzles to be analyzed and organized.
+
+Think of your inner identity as an elite architect building an impregnable stone fortress on top of a mountain. You have an incredible depth of perception (Scorpio Sun) paired with an inner craving for resilience and competence (Capricorn Moon). You don't just feel things; you master them. You are self-reliant, exceptionally observant, and deeply private about your inner world.
+
+### Day-in-the-Life Reality
+* **In Public/Stranger Settings:** When you attend a neighborhood gathering surrounded by acquaintances, you project a calm, unshakable vibe. You don’t wear your emotions on your sleeve or dominate the conversation with small talk. Instead, you sit back like a quiet master detective, warmly observing the group dynamics while keeping your emotional drawbridge safely raised.
+* **In Private/Safe Circle Settings:** Once you return home to your favorite human or intimate confidant, that polite boundary gently melts away. In your secure sanctuary, you willingly open the fortress doors. You share profound emotional truths and deeply perceptive observations about life, showing a warm, protective loyalty that strangers never get to see—though you still prefer discussing constructive solutions over simply lingering in sadness.
+
+---
+
+# Part 2: The Vessel & Steersman (Synthesizing Ascendant, Ruler, and Dignities)
+
+Now let's talk about how you navigate the world. Your **Ascendant** (the zodiac sign rising on the eastern horizon at the moment of your birth) acts as the outer hull and steering wheel of your life's ship. You have a Leo Ascendant. In popular astrology, Leo rising is stereotyped as a loud, theatrical entertainer craving the spotlight. But we must throw that stereotype right out the window for you!
+
+Why? Because in traditional mechanics, the ruler of your Ascendant—the Sun, whom we call the **Steersman** (the captain guiding your ship)—is located in your 4th House (the deep, hidden realm of home, roots, and sanctuary). On top of that, you were born during a **Nocturnal Chart** (a night birth where night-time planets like the Moon and Venus lead the supportive work shift). Your Steersman is riding alongside Saturn (the planet of structure and discipline, acting like a cautious traffic inspector). Because this Saturn influence is mathematically **Mild**, it doesn't build icy walls; rather, it gives your captain a mature, wise hesitation before making a move.
+
+You also have Venus and Jupiter in **Domicile** (a joyful state where planets reside comfortably in their own home signs, giving them immense strength). This gives you immense creative warmth and conversational charm, but because your captain drives from a private house, your true kingdom is behind closed doors, not out on a public stage.
+
+### Day-in-the-Life Reality
+* **In Public/Stranger Settings:** At a bustling downtown cafe or local festival, your "Leo outer hull" gives you a radiant, quiet dignity. People naturally respect your presence, but you aren't fighting for the microphone or trying to be the center of attention. You navigate crowds with a pleasant, measured caution—like a wise captain double-checking the weather dials—preferring to linger comfortably on the edge of the excitement.
+* **In Private/Safe Circle Settings:** Inside the four walls of your own home, your genuine sovereignty truly shines. When you invite your trusted inner circle over for a casual dinner or game night, you transform into the ultimate host. Thanks to that rich, happy Jupiter, you shower your friends with warm hospitality, laughter, and generous comfort, ruling your cozy sanctuary with quiet grace.
+
+---
+
+# Part 3: Tension & Growth (Synthesizing Aspects & the Pain Body)
+
+Our personal growth always springs from internal frictions. In astrology, these frictions show up as **Aspects** (specific geometric angles and conversations between planets). You have a powerful **Conjunction** (planets sitting side-by-side in the same sign, fusing their energies together) between your Sun, Mercury, and Saturn in your private 4th house. Here, your Mercury is **Combust** (sitting so very close to the Sun that its visible light is eclipsed by solar fire). This makes your mind function like a secretive, top-tier research laboratory. Your thoughts run brilliant and deep beneath the surface, but you rarely show your unfinished workings to the outside world.
+
+You also experience a **Square** (a sharp 90-degree angle creating internal push-pull friction) between your Capricorn Moon and Venus in Libra. Imagine throwing a delightful, affectionate dinner party (Venus), while simultaneously feeling a sudden internal urge to lock the front gate so your peace of mind isn't disturbed (Moon). This creates a fascinating developmental tug-of-war between longing for deep romantic closeness and feeling safer when you rely solely on your own emotional composure. 
+
+To keep your emotional armor (your "Pain Body") from turning feelings into analytical tasks or retreating into brooding overthink, your system craves constructive releases. With a dynamic energy spark from Mars squared by Jupiter, you thrive when using **archetypal safe outlets**—such as structured creative hobbies, tactile artistic projects, or disciplined physical mindfulness routines—to channel your intense internal energy into beautiful, tangible expression.
+
+### Day-in-the-Life Reality
+* **In Public/Stranger Settings:** When emotional stress or social friction pops up at a casual gathering, your mild protective armor clicks into gear effortlessly. You don't explode with anger or freeze in icy silence. Instead, your Capricorn emotional instincts quietly shift you into a composed, capable trouble-shooter. You radiate an untroubled calm that reassures everyone around you, even while your deep internal laboratory is secretly running a mile a minute.
+* **In Private/Safe Circle Settings:** In the safe embrace of your romantic partner or dearest friend, you practice laying down that need for complete independence. Instead of trying to instantly dissect a sensitive feeling or conquer a vulnerable moment like a chores list, you take a breath and share the honest emotion. By balancing your energy through a dedicated creative pursuit or quiet physical ritual, you realize that letting loved ones past your defensive walls doesn't weaken your fortress—it fills it with the warmth you secretly crave.
+
+---
+
+# Summary of Your Astrological Blueprint
+
+* **Your Archetype: The Sovereign of the Sanctuary**
+You are a dignified, intensely perceptive intuitive builder who creates true emotional mastery, richness, and security from inside your private domain rather than seeking validation in the public spotlight.
+* **Your Superpower: Unshakable Calm Under Pressure**
+You possess the rare ability to marry incredible emotional depth with rock-solid practical composure, making you a protective, grounded pillar of strength who can gracefully weather any personal storm.
+* **Your Core Lesson: Embracing Soft Vulnerability**
+Learning that you don't always have to be entirely self-sufficient, nor do you need to treat vulnerable emotional moments like structural problems to be solved; letting trusted loved ones inside your gates simply deepens your peace without threatening your independence.
\ No newline at end of file

```

--------------------------------------------------------------------------------

## Commit 3: d7b3b8d

```diff
commit d7b3b8d600a4a75135fd900536ec800af7d0a143
Author: Shivapuri <142108173+Shivapuri@users.noreply.github.com>
Date:   Sun Aug 2 17:50:08 2026 +0530

    test(rag): Establish formal QA & Testing Mandate and implement RAG Quality Evaluation test suite

diff --git a/Gemini.md b/Gemini.md
index 0cc3f9f..3352457 100644
--- a/Gemini.md
+++ b/Gemini.md
@@ -65,6 +65,14 @@ Alternatively, execute the Python calculation generator directly from [`jyotish/
 For AI agent instructions regarding chart interpretation, strictly follow the XML prompt files located in the `/prompts/` directory. Do not use outdated inline prompts.
 
 
+---
+
+## Core Directive: QA & Testing Standards
+Every substantial new feature, architectural change, or data ingestion pipeline added to this repository MUST be accompanied by an automated test script. 
+1. Mathematical Engine updates must be verified against Swiss Ephemeris / Jyotishganit baseline scripts (e.g., `bulk_test_engine.py`).
+2. Vector Database (RAG) updates must be verified for both functionality (does it return text?) and RELEVANCE (does the text contain the correct astrological concepts?) using the RAG Quality Evaluation suite. 
+Do not commit major logic changes without providing a way to programmatically test them.
+
 ---
 
 ## Technical Details & Constraints
@@ -75,3 +83,4 @@ For AI agent instructions regarding chart interpretation, strictly follow the XM
   * **Vedic DB**: Uses Chroma DB in `rag/chroma_jyotish_db/` with HuggingFace embeddings (`all-MiniLM-L6-v2`) for local retrieval of classical BPHS shlokas and VedAstro rules (`rag/fetch_jyotish_data.py` & `rag/build_jyotish_rag.py`).
 
 
+
diff --git a/README.md b/README.md
index 2c2abe3..ff33661 100644
--- a/README.md
+++ b/README.md
@@ -35,6 +35,11 @@ Both engines feature robust, automated QA pipelines capable of stress-testing th
 python scripts/run_western_pipeline.py --name "User" --year 1983 --month 11 --day 10 --hour 4 --minute 20 --city "Georgsmarienhütte" --country "DE"
 ```
 
+**Test Vector Database Retrieval Quality:**
+```bash
+python tests/test_rag_quality.py
+```
+
 **Bulk Stress Test the Western Engine (10,000 Charts):**
 ```bash
 python western/bulk_test_engine.py
@@ -45,3 +50,4 @@ python western/bulk_test_engine.py
 python jyotish/bulk_test_jyotish.py
 ```
 
+
diff --git a/tests/test_rag_quality.py b/tests/test_rag_quality.py
new file mode 100644
index 0000000..a4194d8
--- /dev/null
+++ b/tests/test_rag_quality.py
@@ -0,0 +1,126 @@
+import os
+import sys
+import time
+from typing import List, Dict
+
+# Ensure project root is in sys.path
+BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
+if BASE_DIR not in sys.path:
+    sys.path.insert(0, BASE_DIR)
+
+from langchain_chroma import Chroma
+from langchain_huggingface import HuggingFaceEmbeddings
+
+MODERN_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_modern_db")
+STRUCT_DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_structural_db")
+
+TEST_CASES = [
+    {
+        "name": "Modern DB: Sun in Scorpio",
+        "db_path": MODERN_DB_DIR,
+        "query": "Sun in Scorpio core identity and psychology",
+        "expected_keywords": ["power", "transform", "regeneration", "desire", "energy", "psyche", "solar"]
+    },
+    {
+        "name": "Modern DB: Moon in Capricorn",
+        "db_path": MODERN_DB_DIR,
+        "query": "Moon in Capricorn reigning emotional need",
+        "expected_keywords": ["emotional", "need", "security", "reserve", "psyche", "feeling", "nature"]
+    },
+    {
+        "name": "Modern DB: Pain Body (Saturn/Venus)",
+        "db_path": MODERN_DB_DIR,
+        "query": "Saturn conjunct Venus emotional defense and pain body",
+        "expected_keywords": ["saturn", "venus", "relationship", "love", "defense", "fear", "expression"]
+    },
+    {
+        "name": "Structural DB: Taurus Ascendant",
+        "db_path": STRUCT_DB_DIR,
+        "query": "Taurus Ascendant physical vehicle and temperament",
+        "expected_keywords": ["ascendant", "persona", "personality", "character", "appearance", "taurus", "image"]
+    },
+    {
+        "name": "Structural DB: Aversion",
+        "db_path": STRUCT_DB_DIR,
+        "query": "Chart ruler in the 8th house aversion",
+        "expected_keywords": ["aversion", "eighth", "twelfth", "sixth", "ruler", "house", "blind"]
+    }
+]
+
+
+def run_quality_tests():
+    print("======================================================================")
+    print(" 🧪 RUNNING RAG RETRIEVAL QUALITY & RELEVANCE SUITE")
+    print("======================================================================")
+    
+    if not os.path.exists(MODERN_DB_DIR) or not os.path.exists(STRUCT_DB_DIR):
+        print("❌ Error: Vector databases not found. Build them first.")
+        return
+
+    print("Loading Embedding Model (all-MiniLM-L6-v2)...")
+    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
+    
+    # Load DBs
+    dbs = {
+        MODERN_DB_DIR: Chroma(persist_directory=MODERN_DB_DIR, embedding_function=embedding_model),
+        STRUCT_DB_DIR: Chroma(persist_directory=STRUCT_DB_DIR, embedding_function=embedding_model)
+    }
+
+    total_tests = len(TEST_CASES)
+    passed_tests = 0
+    start_time = time.time()
+
+    for i, test in enumerate(TEST_CASES, 1):
+        print(f"\n[Test {i}/{total_tests}] {test['name']}")
+        print(f"  Query: '{test['query']}'")
+        
+        db = dbs[test['db_path']]
+        results = db.similarity_search(test['query'], k=4)
+        
+        if not results:
+            print("  ❌ FAIL: No results returned.")
+            continue
+            
+        combined_text = " ".join([doc.page_content.lower() for doc in results])
+        
+        # Calculate relevance
+        hits = 0
+        found_words = []
+        missed_words = []
+        
+        for kw in test['expected_keywords']:
+            if kw.lower() in combined_text:
+                hits += 1
+                found_words.append(kw)
+            else:
+                missed_words.append(kw)
+                
+        relevance_score = (hits / len(test['expected_keywords'])) * 100
+        
+        print(f"  Found Keywords: {found_words}")
+        if missed_words:
+            print(f"  Missed Keywords: {missed_words}")
+        
+        if relevance_score >= 40.0:  # 40% keyword hit rate is a very strong semantic signal for RAG
+            print(f"  ✅ PASS: Relevance Score {relevance_score:.1f}%")
+            passed_tests += 1
+        else:
+            print(f"  ❌ FAIL: Relevance Score {relevance_score:.1f}% (Below 40% threshold)")
+
+    duration = time.time() - start_time
+    print("\n======================================================================")
+    print(" 📊 QA TEST SUMMARY")
+    print("======================================================================")
+    print(f" Total Tests Run : {total_tests}")
+    print(f" Passed          : {passed_tests}")
+    print(f" Failed          : {total_tests - passed_tests}")
+    print(f" Time Taken      : {duration:.2f} seconds")
+    print("======================================================================")
+    
+    if passed_tests == total_tests:
+        print("🏆 SUCCESS: All RAG databases are highly functional and relevant.")
+    else:
+        print("⚠️ WARNING: Some queries returned low-relevance documents. Database tuning may be required.")
+
+if __name__ == "__main__":
+    run_quality_tests()

```

--------------------------------------------------------------------------------

