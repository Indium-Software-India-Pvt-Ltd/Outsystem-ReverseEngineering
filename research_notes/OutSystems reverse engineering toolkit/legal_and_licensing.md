# Legal, Contractual and Licensing Constraints on Reverse Engineering OutSystems Applications and the OutSystems Platform

> **This is research, not legal advice.** Nothing here is a legal opinion and no solicitor/attorney-client relationship is created. Public standard-form terms are quoted below; **a specific customer's signed Order / negotiated Master Subscription Agreement may differ materially** from the published versions and takes precedence for that customer. Any organisation acting on this must have its own counsel read its own executed contract.
>
> **Currency of documents (as checked 2026-10-21):**
> - OutSystems Master Subscription Agreement (MSA) — page states **"Updated: February 1, 2026"**
> - OutSystems End-user Licensing Agreement (EULA) — page states **"Updated: Monday, July 8, 2024"**
> - Directive 2009/24/EC — in force since 2009, unamended; a May 2025 EU "non-paper" discusses possible reform but nothing is adopted
> - IBM v LzLabs liability judgment — 10 March 2025; a Court of Appeal decision ([2025] EWCA Civ 842) exists but its scope was not verified

---

## Q1. What do the OutSystems license agreements say, and where are they published?

### Takeaway
OutSystems publishes a full set of standard-form legal documents at `outsystems.com/legal`. Both the Master Subscription Agreement (MSA) and the End-user Licensing Agreement (EULA) contain explicit no-reverse-engineering / no-decompilation clauses, and both are expressly qualified by the words **"except to the extent expressly permitted by applicable law"** — which is the hook on which the EU statutory exceptions hang.

### Cited Findings

**Where the documents live.** The legal index page lists 16 agreements — [OutSystems Legal](https://www.outsystems.com/legal):

| Document | URL |
|---|---|
| Master Subscription Agreement (MSA) | https://www.outsystems.com/legal/outsystems-msa (also served at https://www.outsystems.com/legal/master-subscription-agreement/) |
| End-user Licensing Agreement (EULA) | https://www.outsystems.com/legal/end-user-licensing-agreement |
| Data Processing Agreement (DPA) | https://www.outsystems.com/legal/outsystems-msa-data-processing-agreement |
| Subscription Compliance Terms | https://www.outsystems.com/legal/subscription-compliance-terms |
| ODC and O11 Cloud Resource Capacity Fair Usage Limits | https://www.outsystems.com/legal/fair-use-limits |
| Support terms and SLAs for OutSystems 11 and ODC | https://www.outsystems.com/legal/success-support-terms-and-service-level-agreements-sla-of-the-outsystems11-and-odc-software |
| Software License Trial Agreement | https://www.outsystems.com/legal/trial-terms |
| Early Access Software Test Agreement | https://www.outsystems.com/legal/eap-agreement-terms-and-conditions |
| Channel Partner Agreement | https://www.outsystems.com/legal/partner-agreement |
| Consultancy Services Agreement | https://www.outsystems.com/legal/consultancy-services-agreement |
| Website Terms of Use | https://www.outsystems.com/legal/terms-of-use |
| Repository Terms of Use | https://www.outsystems.com/legal/repository-terms-of-use |
| Contracting company, governing law and jurisdiction | https://www.outsystems.com/legal/governing-law-jurisdiction |

- **There is no standalone "ODC Terms of Service" document.** ODC is governed by the same MSA; the only ODC-specific published documents are the Fair Usage Limits page and the combined O11/ODC support SLA — [OutSystems Legal index](https://www.outsystems.com/legal); [ODC and O11 Fair Usage Limits](https://www.outsystems.com/legal/fair-use-limits)
- **The Website Terms of Use expressly do NOT govern subscription use** — the page states it "is not related to the OutSystems subscription agreement" — [OutSystems Website Terms of Use](https://www.outsystems.com/legal/terms-of-use)

**MSA §3.2 "Restrictions of Use"** — the customer may not, inter alia, *"decompile, disassemble, reverse engineer, or otherwise attempt to derive source code from the Software"* — [OutSystems MSA, updated Feb 1 2026](https://www.outsystems.com/legal/master-subscription-agreement/). §3.2 contains eleven enumerated restrictions (i)–(xi), covering: (i) modifying/translating/exporting/adapting the Software; (ii) creating derivative works beyond Applications deployed under a Subscription; (iii) removing Software markings or IP notices; (iv) **circumventing access or usage-measurement controls**; (v) using the Software *"to provide third party training or for the purpose of building or operating a competitive product"*; (vi) disclosing benchmark results; (vii) running production Applications from non-production environments; (viii) any use violating law or the Agreement; (ix)–(xi) sharing the Software with third parties, selling/distributing deployed Applications, hosting or operating Applications for third parties — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/)

**MSA §3.1 License grant** — a *"limited, non-exclusive, non-transferable license, without rights to sublicense, to use the Software during the Subscription Term"*, for building Applications for the Customer's own business processes — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/)

**EULA §3.2** — *"Except to the extent expressly permitted by applicable law, You may not decompile, disassemble, reverse engineer, or otherwise attempt to derive source code from the Software, in whole or in part."* — [OutSystems EULA, updated July 8 2024](https://www.outsystems.com/legal/end-user-licensing-agreement/)

**EULA §4.1 (broader, and the operative one)** — *"Except as and only to the extent permitted by applicable law, or by licensing terms governing use of open-sourced components included with the Software, You may not copy, decompile, reverse engineer, disassemble, attempt to derive the source code of, decrypt, modify, or create derivative works of the Software or Software updates, or any part thereof."* — [OutSystems EULA](https://www.outsystems.com/legal/end-user-licensing-agreement/)

**EULA §3.1** — *"This Software is licensed, not sold."* and *"The rights of use granted shall not include any rights to the source code of the Software."* — [OutSystems EULA](https://www.outsystems.com/legal/end-user-licensing-agreement/)

- The identical reverse-engineering language appears on the French, German, Brazilian-Portuguese and Japanese EULA pages, indicating it is global standard-form text — e.g. [EULA (de-de)](https://www.outsystems.com/de-de/legal/end-user-licensing-agreement/), [EULA (fr-fr)](https://www.outsystems.com/fr-fr/legal/end-user-licensing-agreement/), [EULA (pt-br)](https://www.outsystems.com/pt-br/legal/end-user-licensing-agreement/), [EULA (ja-jp)](https://www.outsystems.com/ja-jp/legal/end-user-licensing-agreement/)
- The **Subscription Compliance Terms** are *"incorporated by reference into the Master Subscription Agreement"* and govern renewals/expansions; a **30-day grace period** applies before suspension or deletion, and the ~60-day renewal notice is described as voluntary and "not a contractual obligation" — [OutSystems Subscription Compliance Terms](https://www.outsystems.com/legal/subscription-compliance-terms/)

### Inferences
- The *"except to the extent expressly permitted by applicable law"* carve-out is deliberate and is the standard way vendors acknowledge mandatory statutory exceptions (EU Art. 5(3)/6, US §1201(f), §117) that they cannot contract around. It means the clause is **not** an absolute bar in the EU/EEA/UK.
- Restriction (iv) — circumventing access or usage-measurement controls — matters independently of copyright: if an extraction toolkit has to defeat licence enforcement, encryption of OML, or metering, that is a separate contractual breach and in the US potentially a §1201(a) circumvention claim, even where the underlying content is the customer's own.
- Restriction (v) — "building or operating a competitive product" — is the clause most likely to be invoked against a *reusable, distributable* OutSystems→X migration toolkit, as distinct from an internal one-off extraction.

### Gaps
- Could not retrieve full verbatim text of each of MSA §3.2(i)–(xi) and §8.4; the fetch tool caps quotations at ~125 characters per excerpt. **The report writer should not present the enumerated list as verbatim** — it is an accurate paraphrase of the eleven items. Anyone relying on it must read the page directly.
- The MSA page shows no section-level anchors confirming whether a separate reverse-engineering sub-item is numbered within (i)–(xi) or stated separately; the fetch returned it as an additional sentence.
- No published OutSystems "ODC-specific" terms exist to compare; could not confirm whether ODC order forms layer extra terms.

---

## Q2. Do the clauses reach the customer's own applications and .oml packages? Who owns what?

### Takeaway
**The IP ownership split is clear and favourable to the customer: OutSystems owns the Software; the customer owns the Applications and Customer Content.** But there is a genuine, material drafting tension: the MSA's definition of **"Software" expressly includes "OutSystems Markup Language and low-code models"** — i.e. the OML/model layer itself is claimed as OutSystems IP, *except* to the extent it incorporates Customer Content. So an .oml file is a hybrid object under these terms, not unambiguously "yours".

### Cited Findings

**Customer-side ownership.**
- MSA §6 ("Customer's Intellectual Property"): *"All Intellectual Property Rights in and to Applications and Customer Content are owned by Customer"*; the customer also owns Deliverables, subject to payment of agreed Fees and Expenses — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/)
- EULA §4.2: *"All Intellectual Property Rights in and to Applications and End-User Content are owned by End-User, and shall, subject to the terms of this EULA, remain vested in End-User."* — [OutSystems EULA](https://www.outsystems.com/legal/end-user-licensing-agreement/)

**Vendor-side ownership.**
- MSA §6 ("OutSystems' Intellectual Property"): *"All Intellectual Property Rights in and to the Software and Professional Services Tools are owned by OutSystems."* Customers acquire no proprietary interest in them — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/)
- EULA §4.1: *"All Intellectual Property Rights in and to the Software are owned by OutSystems and shall, notwithstanding the terms of this EULA, remain vested in OutSystems."* — [OutSystems EULA](https://www.outsystems.com/legal/end-user-licensing-agreement/)

**The critical definitions (MSA §1), quoted verbatim:**
- **"Application"** = *"the computer application developed by Customer through the use of the Software."* — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/)
- **"Software"** = *"(i) the applicable OutSystems software products described in the applicable Order"* … *"(ii) components generated by OutSystems software products to facilitate the creation of Applications"*, *"including without limitation OutSystems Markup Language and low-code models"*, *"to the extent those components do not incorporate Customer Content"* … *"(iii) the Cloud hosting platform used by OutSystems to provide OutSystems software products as a platform as a service"* … *"(iv) all updates to OutSystems software products provided as part of Support and Updates"* … *"(v) the Documentation"* — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/)
- **"Customer Content"** = *"software (including machine images), online services, features, technology, data, text, audio, video, images, Personal Data, or other content supplied by Customer or by third-parties on behalf of Customer in connection with an Application."* — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/)
- The MSA uses **"Applications"**, not "Customer Applications"; and **"Customer Content"**, not "Customer Data" (though "Customer Data" appears untyped in §9 "Customer Responsibility") — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/)

### Inferences (flagged as interpretation, not quotation)
1. **The restriction is drafted against "the Software", not against "Applications".** On a plain reading, §3.2's no-reverse-engineering clause does not prohibit the customer from analysing, parsing or documenting its own **Application** — which the customer owns outright under §6. Documenting your own business logic is not "deriving source code from the Software".
2. **But "Software" (ii) pulls the OML format and the low-code model into the vendor's IP.** This is the single most important finding for an OML-parsing toolkit. OutSystems's drafting position is that the *model/markup layer generated by its products* is its own IP, carved back only "to the extent those components do not incorporate Customer Content". An .oml file for a real application plainly contains both: platform-generated model structure (claimed as Software) and the customer's logic, entity definitions, text, queries and assets (Customer Content / the Application).
3. Consequently, there is a reasonable argument in both directions, and the risk is not symmetric across activities:
   - **Reading an .oml you own to extract your own logic, entities, screens and SQL** → strongest position. You own the Application and the Customer Content; §6 says so; this is not deriving the Software's source code.
   - **Reverse engineering the .oml *container format itself* and publishing a general-purpose OML parser/spec** → weakest position. That is directly characterisable as deriving the structure of something the MSA defines as "Software", and if the parser is then shipped as a migration product it also engages restriction (v) ("building or operating a competitive product").
   - **Decompiling Platform Server / Service Studio / OutSystems runtime assemblies** → squarely prohibited by §3.2 and EULA §4.1, subject only to statutory exceptions.
4. The clause binds **the contracting customer and anyone the customer allows** ("will not allow any third party to" in EULA §3.2). A third-party migration vendor engaged by the customer is therefore inside the contractual perimeter — the customer can breach through its contractor.

### Gaps
- I found **no public OutSystems statement, FAQ or support article** addressing whether customers may parse their own OML files with third-party tools. No published vendor guidance either permitting or prohibiting it was located.
- Whether the OML file format is protected by a technological protection measure (encryption/obfuscation) in current versions was not researched here — it is legally material in the US (DMCA §1201(a)) and should be verified empirically by the technical workstream.
- Whether individual negotiated Orders commonly add or soften these terms is unknown; no sample negotiated OutSystems contracts were found in public sources.

---

## Q3. Does OutSystems make data portability / exit commitments?

### Takeaway
Yes — a contractual **"Detachment"** right exists in both the MSA and the EULA, giving the customer a copy of its Applications **in source code format** on termination. It is narrow, time-boxed (30 days after the Subscription Term), conditional on paying all outstanding fees, and in practice appears to be an O11-era mechanism with no confirmed public ODC equivalent.

### Cited Findings
- **MSA §8.4(ii) "Effect of Termination"**: on termination or expiry, *"Customer is entitled to (1) detach a copy of its Applications ("Detachment") in source code format"*, plus its Customer Content, "subject to the Documentation's specifications and limitations". Conditions: written notice of the Detachment request; payment of all remaining Fees due; and the process must be completed *"within 30 days following the end of the applicable Subscription Term"*. After Detachment the customer must de-install and/or destroy the Software — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/)
- **MSA §8.4(i)**: on termination, Subscriptions are automatically cancelled and access ends except as provided in §8.4(ii) — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/)
- **EULA §6.2(ii)** mirrors this: after termination the customer may *"detach a copy of Your Applications ("Detachment") in source code format"*, subject to Documentation specifications and limitations — [OutSystems EULA](https://www.outsystems.com/legal/end-user-licensing-agreement/)
- **No source-code escrow, no ongoing (in-term) export right, and no general data-portability clause** appears in the published MSA. §7 ("Destruction or Return") concerns Confidential Information, and §12.4 ("Export and Sanctions Laws") is about export control, not data export — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/)
- A UK G-Cloud listing by an OutSystems partner states the platform "provides a documented Detachment Process upon contract termination" — reseller marketing, not an OutSystems source — [Digital Marketplace listing](https://www.applytosupply.digitalmarketplace.service.gov.uk/g-cloud/services/462854692013187)

**Practical mechanics (community sources — lower reliability, clearly labelled):**
- Detach is described by community members as available only for paid/enterprise environments, not the free Personal Environment; the customer notifies OutSystems that the subscription is ending and OutSystems then enables the detach function; it is performed from the production environment — [OutSystems Forum: "About the detach process"](https://www.outsystems.com/forums/discussion/66302/about-the-detach-process/); [OutSystems Forum: "Detaching source code"](https://www.outsystems.com/forums/discussion/34743/detaching-source-code/)
- Output is reported as a Visual Studio `.sln` solution deployable to IIS; one step requires querying the OutSystems metadata database (`OSSYS_SERVER`) — [OutSystems Forum: "Experience in detaching"](https://www.outsystems.com/forums/discussion/84036/experience-in-detaching/)
- **For ODC**, a forum answer states there is "currently no equivalent public mechanism that generates a traditional .NET solution package similar to O11", and that ODC detachment is handled contractually with OutSystems — [OutSystems Forum: "Detachment process from OutSystems ODC"](https://www.outsystems.com/forums/discussion/105782/detachment-process-from-outsystems-odc-any-guidance-or-experience/)
- For self-managed O11 installations, community posts describe generated C#/ASPX/CSS/JS files being readable on the Platform Server filesystem via web server and IIS access — explicitly "not possible if you are on an enterprise OutSystems cloud environment" — [OutSystems Forum: "How extracting web and backend application source code"](https://www.outsystems.com/forums/discussion/61645/how-extracting-web-and-backend-application-source-code); [OutSystems Forum: "OutSystems export source code for code scanning"](https://www.outsystems.com/forums/discussion/45764/outsystems-export-source-code-for-code-scanning)
- A community Forge asset, **"SourceCode Download (O11)"**, downloads module source code for SAST scanning, licensed BSD-3 — [OutSystems Forge: SourceCode Download O11](https://www.outsystems.com/forge/component-overview/20411/sourcecode-download-o11)

### Inferences
- The Detachment right is the **vendor-sanctioned exit path** and is strategically important: using it (or formally requesting exit assistance) converts a potentially contentious reverse-engineering exercise into an authorised one. It should be the first option explored in any migration project, and it should be invoked *before* the 30-day post-term window closes.
- The 30-day window and "pay all remaining Fees" precondition mean Detachment is a poor fit for a migration that runs in parallel with a live subscription. Organisations wanting source during the term should negotiate an **in-term extraction/portability right into the Order**, because the standard MSA does not grant one.
- The ODC gap is the key practical risk: if the published standard mechanism is O11-only, ODC customers have a contractual Detachment entitlement whose technical implementation is undocumented publicly — a strong reason to get it specified in writing from the account team early.
- Existence of the Detachment right cuts **in favour** of a customer arguing that extracting its own application is within the spirit of the bargain; it cuts **against** an argument that reverse engineering was "necessary" if Detachment was available and not used (relevant to the EU Art. 6 condition that the information was "not previously readily available").

### Gaps
- The official OutSystems detach documentation page could not be retrieved (`success.outsystems.com/support/licensing/detach_process_for_outsystems_11/` returned **HTTP 404**). The precise list of what is and is not included in a detached package — critically, **whether OutSystems runtime DLLs are included and on what licence terms after termination** — is therefore **unverified**. This is an important open question; it should be asked directly of OutSystems.
- No published statement found on whether detached code may be modified, redeployed indefinitely, or carries a perpetual runtime licence.
- No evidence of a source-code escrow offering.

---

## Q4. Statutory exceptions and their interaction with contract terms

### Takeaway
The EU/UK position is materially stronger for the customer than the US position: **Directive 2009/24/EC makes contract terms contrary to Articles 5(2), 5(3) and 6 null and void**, so OutSystems cannot contract away back-up copying, observation/study/testing, or decompilation-for-interoperability. In the US there is no equivalent anti-override rule — fair use and §1201(f) limit *copyright* liability but generally do **not** excuse *breach of contract*, as the SAS v WPL US litigation shows. Other jurisdictions (e.g. much of Asia, the Gulf) have narrower or no such exceptions; do not assume the EU position travels.

### Cited Findings — EU / UK

**Directive 2009/24/EC Article 6 (Decompilation)** — authorisation of the rightholder is not required where reproduction of the code and translation of its form *"are indispensable to obtain the information necessary to achieve the interoperability of an independently created computer program with other programs"*, subject to three conditions: the acts are performed by the licensee or a person having a right to use a copy, or a person authorised on their behalf; **the information necessary to achieve interoperability has not previously been readily available** to those persons; and the acts are **confined to the parts of the original program which are necessary** to achieve interoperability — [Directive 2009/24/EC Art. 6, legislation.gov.uk](https://www.legislation.gov.uk/eudr/2009/24/article/6)

**Article 6(2) limits** — information obtained may not be used for goals other than achieving interoperability of the independently created program; may not be given to others except where necessary for that interoperability; and may not be used **for the development, production or marketing of a computer program substantially similar in its expression**, or for any other act infringing copyright — [Directive 2009/24/EC Art. 6(2)](https://www.legislation.gov.uk/eudr/2009/24/article/6/data.html)

**The anti-override rule.** Article 8 / Recital 17 of the Directive: contractual provisions contrary to the decompilation provisions, and to the back-up copy and observation/study/testing exceptions, **"should be null and void"** — [Directive 2009/24/EC (full text), legislation.gov.uk](https://www.legislation.gov.uk/eudr/2009/24/body/adopted?view=plain). Recital 17 also states the Directive does not affect EU competition rules where a dominant supplier refuses to supply information needed for interoperability — [ibid.](https://www.legislation.gov.uk/eudr/2009/24/data.htm)

**SAS Institute v World Programming, CJEU Case C-406/10 (2012)** — held that **copyright protection does not extend to the functionality, the programming language, or the file format** of a computer program; and that in so far as licence terms sought to restrict the Article 5(3) observation/study/testing exception, **those terms were void**. But the Court also confirmed the exception does **not** extend to accessing source code or using a decompiler to analyse that code — [CMS Law: "SAS v WPL — who dares loses"](https://cms.law/en/gbr/legal-updates/sas-v-wpl-who-dares-loses); [SCL: Court of Appeal Judgment in SAS v WPL](https://www.scl.org/2954-court-of-appeal-judgment-in-sas-v-wpl/); [8 New Square: SAS Institute Inc v World Programming Ltd [2013] EWCA Civ 1482](https://8newsquare.co.uk/sas-institute-inc-v-world-programming-ltd-2013-ewca-civ-1482/)
- On the basis of that CJEU ruling, the UK High Court entered final judgment for WPL in 2013 — [Project DisCo analysis](https://project-disco.org/intellectual-property/102417-in-sas-decision-appellate-court-dodges-addressing-oracle/)
- **However**, in the parallel US proceedings the Fourth Circuit affirmed that **WPL breached its licence agreement** — *"the contractual terms at issue are unambiguous and ... SAS has shown that WPL violated those terms. We thus affirm the district court's judgment finding WPL liable for breach of the license agreement."* — [SAS v WPL, 4th Cir. opinion (EFF copy)](https://eff.org/files/2021/10/14/sas_v._wpl_ca4-opinion_10-24-2017.pdf)
- A May 2025 EU non-paper discusses updating Directive 2009/24/EC (including clarifications for FOSS codebases) while stating it would not change the interoperability philosophy of recitals 10 and 15. **This is a discussion document, not adopted law** — [Interoperable Europe non-paper, May 2025](https://interoperable-europe.ec.europa.eu/sites/default/files/discussion/attachment/2025-05/Non-paper%20PES%202025-05-09%20on%20updating%20Directive%202009-24-EC%20v01.pdf)

### Cited Findings — US

**17 U.S.C. §1201(a)(1)(A)** — *"No person shall circumvent a technological measure that effectively controls access to a work protected under this title."* — [17 U.S.C. §1201, Cornell LII](https://www.law.cornell.edu/uscode/text/17/1201)

**17 U.S.C. §1201(f) "Reverse engineering"** (paraphrased from the statute; quotation length was tool-limited):
- **(f)(1)** a person who has **lawfully obtained the right to use a copy** of a computer program may circumvent an access control for *"the sole purpose of identifying and analyzing those elements of the program"* necessary to achieve interoperability of an independently created program, provided the acts do not constitute infringement
- **(f)(2)** notwithstanding (a)(2) and (b), a person may develop and employ technological means to circumvent for the (f)(1) purpose or to enable interoperability, where those means are necessary and do not constitute infringement
- **(f)(3)** information or means obtained may be made available to others **"solely for the purpose of enabling interoperability"**, where doing so does not constitute infringement or violate other applicable law
- **(f)(4)** *"interoperability"* is defined as the ability of computer programs to exchange information and mutually to use the information which has been exchanged
— [17 U.S.C. §1201, Cornell LII](https://www.law.cornell.edu/uscode/text/17/1201)

**The fair-use reverse-engineering line:**
- **Sega Enterprises Ltd. v. Accolade, Inc., 977 F.2d 1510 (9th Cir. 1992)** — disassembly of object code to learn unprotected functional elements required for console compatibility was **fair use**; the court held the defendant's "reverse engineering" of the plaintiff's computer program qualified as fair use — [U.S. Copyright Office, Fair Use Index summary](https://www.copyright.gov/fair-use/summaries/segaenters-accolade-9thcir1992.pdf)
- **Atari Games Corp. v. Nintendo (Fed. Cir. 1992)** — the contrast case: deprocessing chips to learn unprotected ideas was permissible, but **copying beyond what was necessary** to understand the 10NES program was infringement; Atari's decompilation was ultimately found improper — [Duke IP course materials](https://courses.cs.duke.edu/cps182s/fall02/cscopyright/Copyrights/Copyright-Fairuse.htm)
- **Sony Computer Entertainment, Inc. v. Connectix Corp., 203 F.3d 596 (9th Cir. 2000)** — intermediate copying during reverse engineering is fair use where necessary to gain access to unprotected functional elements and the resulting product is transformative and non-infringing; the court rejected the district court's "studying" vs "use" distinction as artificial — [Wikipedia: Sony v. Connectix](https://en.wikipedia.org/wiki/Sony_Computer_Entertainment,_Inc._v._Connectix_Corp.); [Patent Arcade case analysis](https://www.patentarcade.com/?p=898)
- Commentary notes Congress endorsed the Sega/Connectix holdings in the DMCA legislative history, and that the reverse-engineering exemption is codified at §1201(f) — [Internet & Technology Law: History of the fair use defense for software](https://www.internetandtechnologylaw.com/history-fair-use-defense-software/)

**Google LLC v. Oracle America, Inc., 593 U.S. 1 (2021)** — decided **5 April 2021, 6–2** (Breyer, J.; Barrett not participating; Thomas dissenting joined by Alito). Oracle alleged Google copied **~11,500 lines** of Java SE declaring code. The Court **assumed "for argument's sake"** the API code was copyrightable and did not decide copyrightability, holding instead that Google's reimplementation of **only the interface** needed so programmers could apply existing skills on a new, transformative platform **was fair use as a matter of law**. It also held fair use is a mixed question — facts reviewed for clear error, legal parts de novo — [Jones Day: Supreme Court Ends Decade-Long Software Copyright Battle](https://www.jonesday.com/en/insights/2021/04/supreme-court-google-wins-copyright-battle); [Faegre Drinker: Supreme Court Decides Google LLC v. Oracle America](https://www.faegredrinker.com/en/insights/publications/2021/4/supreme-court-decides-google-llc-v-oracle-america-inc); [AIPLA summary](https://www.aipla.org/detail/news/2021/04/05/supreme-court-overturns-oracle-copyright-win-regarding-programming-code-holds-fair-use); [Mondaq / Wiley alert](https://www.wiley.law/alert-Supreme-Court-Determines-Copying-of-Software-API-Can-Constitute-Fair-Use)

### Inferences
- **The decisive structural asymmetry:** in the EU/UK, a contract clause purporting to forbid Art. 6 decompilation-for-interoperability is void to that extent, so the customer has a mandatory floor of rights. In the US, fair use and §1201(f) are defences to *copyright and anti-circumvention* claims, not to *breach of contract* — SAS v WPL (4th Cir.) is direct authority that a licensee can lose on contract even where the copyright claim fails. A US-governed OutSystems Order is therefore meaningfully riskier than an EU-governed one for the same technical activity.
- **Governing law matters a lot and must be checked**: OutSystems publishes a separate "Contracting OutSystems Company, governing law and jurisdiction" page ([link](https://www.outsystems.com/legal/governing-law-jurisdiction)), so which entity and law applies is order-specific. A Portuguese/Dutch/EU contracting entity engages the Directive; a US entity may not.
- **Art. 6's conditions are demanding and map badly onto migration**: (a) the information must not have been "previously readily available" — the existence of the Detachment process and documented APIs weakens this; (b) acts must be "confined to the parts necessary" for interoperability — a wholesale decompilation of the platform fails this; (c) Art. 6(2) forbids using the information to develop a **substantially similar** program — building a competing low-code runtime would fail, whereas emitting a conventional React/.NET app from your own model probably would not.
- **Google v. Oracle helps the "format and interface" argument** in the US (and SAS C-406/10 helps it in the EU, since file formats and languages are held unprotectable): understanding and reimplementing an *interface or file format* to carry your own data across is the fact pattern most favourably treated by both bodies of law. It does **not** license copying implementation code.
- Art. 5(3) (observation, study and testing during normal lawful use) is the cleanest basis for **inspecting your own running application and its artefacts** — and SAS C-406/10 confirms licence terms cannot restrict it. It does **not** authorise decompilation.

### Gaps
- Could not quote §1201(f) fully verbatim (tool quotation cap). The report writer should treat the (f)(1)–(f)(4) descriptions as close paraphrase and verify against the statute before publishing quoted text.
- Did not verify the exact Article number of the Directive's anti-override provision in the consolidated text (it is stated in Recital 17 and given effect in Art. 8); the report should cite Recital 17 + Art. 8 together rather than asserting one.
- No research done on the current US Copyright Office triennial §1201 exemptions (the 2024 rulemaking cycle) — the permanent §1201(f) exemption was the focus. Worth a separate check if circumvention of a TPM is actually contemplated.
- Non-EU/non-US jurisdictions (UAE, Saudi Arabia, Singapore, India, Japan, Australia) were not researched; their reverse-engineering exceptions differ in scope and some have no mandatory anti-override rule.

---

## Q5. Is decompiling the *generated* .NET/Java assemblies of your own app different from decompiling OutSystems's own runtime DLLs?

### Takeaway
Legally, yes — materially different, and the distinction tracks ownership. Generated assemblies that embody **your** application logic are compiled expressions of an Application you own under MSA §6; decompiling them is closer to reading your own code than to reverse engineering someone else's product. OutSystems platform runtime DLLs are unambiguously "Software" and are the core target of §3.2 / EULA §4.1. **The mixed case is where the real risk sits**, and no public source resolves it.

### Cited Findings
- Ownership basis for the distinction: *"All Intellectual Property Rights in and to Applications and Customer Content are owned by Customer"* (MSA §6) versus *"All Intellectual Property Rights in and to the Software and Professional Services Tools are owned by OutSystems"* (MSA §6) — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/)
- But the "Software" definition reaches *"components generated by OutSystems software products to facilitate the creation of Applications"* — expressly *"including without limitation OutSystems Markup Language and low-code models"* — carved back only *"to the extent those components do not incorporate Customer Content"* — [OutSystems MSA §1](https://www.outsystems.com/legal/master-subscription-agreement/)
- EULA §3.1: *"The rights of use granted shall not include any rights to the source code of the Software."* — [OutSystems EULA](https://www.outsystems.com/legal/end-user-licensing-agreement/)
- US law offers a route for the generated-assembly case independent of the vendor's characterisation: 17 U.S.C. §117(a) permits the owner of a copy of a computer program to make a new copy or adaptation as an **essential step in the utilization of the program** in conjunction with a machine, used in no other manner — [17 U.S.C. §117, Cornell LII](https://www.law.cornell.edu/uscode/text/17/117)
- Generated code is physically accessible on self-managed O11 Platform Servers: community reports describe generated C#, ASPX, CSS and JS files residing in folders on the web/IIS server, accessible only with self-managed installations and "not possible if you are on an enterprise OutSystems cloud environment" — [OutSystems Forum](https://www.outsystems.com/forums/discussion/61645/how-extracting-web-and-backend-application-source-code)
- Atari v. Nintendo establishes the limiting principle for the mixed case in the US: copying **beyond what is necessary** to understand the unprotected elements is infringement — [Duke IP course materials](https://courses.cs.duke.edu/cps182s/fall02/cscopyright/Copyrights/Copyright-Fairuse.htm)

### Inferences (interpretation — no direct authority found on OutSystems specifically)
A defensible three-tier risk model:

1. **Lowest risk — generated code that is purely your application's logic.** Reading generated C#/Java that implements your own screens, actions, aggregates and entity access. You own the Application; §117(a) (US) and Art. 5(3) (EU) support inspection; there is no sensible reading of §3.2 under which documenting your own business rules is "deriving source code from the Software". On a self-managed installation this code is simply present on disk — no circumvention is involved, which also keeps §1201(a) out of play.
2. **Medium risk — the mixed/boundary case.** Generated assemblies that (a) link against `OutSystems.*` runtime libraries, (b) embed OutSystems-authored helper/boilerplate code emitted by the compiler, or (c) reveal the internal structure of the OutSystems runtime through the shape of their calls. Here, reading *your* logic is incidental to reading *their* framework. Two practical mitigations follow directly from the legal tests: **(i) necessity/minimisation** — decompile only the assemblies that carry your logic, not the runtime ones, and stop at the first source that gives you the information (Art. 6 "confined to the parts necessary"; Atari "beyond what is necessary"); **(ii) don't reproduce vendor expression in output** — record the *interface shape* you must call (favoured by Google v. Oracle and SAS C-406/10) and never carry vendor implementation code into the migrated artefact (Art. 6(2) "substantially similar in its expression").
3. **Highest risk — OutSystems's own platform software.** Decompiling Platform Server, Service Studio, Integration Studio, the Deployment Controller, LifeTime, licence-enforcement components, or `OutSystems.*` runtime DLLs. This is the paradigm case §3.2 and EULA §4.1 target. In the EU a narrow Art. 6 interoperability defence is theoretically available and cannot be contracted away, but IBM v LzLabs (below) shows how hard it is to run successfully; in the US there is no anti-override protection and a contract claim survives even if fair use defeats the copyright claim.

Additional inference: **the OML route is generally lower-risk than the decompilation route** for logic extraction, because the OML is a model you authored (even if the *format* is contested) whereas the DLLs are a compiled artefact of the vendor's compiler and runtime. Where both routes give the same information, choosing OML parsing — or better, the Detachment output — reduces exposure. Conversely, if a toolkit decompiles DLLs *because* the OML format is undocumented, that is evidence the interoperability information "was not previously readily available", which strengthens an EU Art. 6 argument.

### Gaps
- **No authority — no case, no OutSystems statement, no law-firm note — was found addressing OutSystems generated assemblies specifically.** The three-tier model above is reasoning by analogy from the contract text and general software-copyright law, and must be labelled as such in the final report.
- Whether OutSystems-generated assemblies are obfuscated or protected by a TPM is unverified and is legally material in the US (§1201(a) vs §1201(f)); the technical workstream should determine this.
- Whether the OutSystems runtime libraries carry a separate redistribution/runtime licence (and what it says about analysis) after Detachment is unverified — the detach documentation page returned 404.
- Whether ODC's compiled output is even reachable by the customer was not confirmed.

---

## Q6. Public disputes, lawsuits or enforcement actions over reverse engineering / migration

### Takeaway
**I found no public dispute, lawsuit or enforcement action by OutSystems — or by Mendix, Salesforce, ServiceNow or Appian — over reverse engineering or migration.** The absence of low-code precedent is itself a finding. However, the closely analogous enterprise-migration line of cases is active and currently **vendor-favourable**: IBM v LzLabs (English High Court, March 2025) is the leading modern decision and it rejected Software Directive defences raised by a migration-tool developer.

### Cited Findings

**IBM United Kingdom Ltd v LzLabs GmbH & Ors [2025] EWHC 532 (TCC)** — judgment of Mrs Justice O'Farrell, handed down **10 March 2025**, 253 pages, trial on liability only:
- The dispute concerned LzLabs' **Software Defined Mainframe (SDM)**, a product for moving mainframe applications to open platforms — [Sifted: IBM lawsuit Zurich startup LzLabs](https://sifted.eu/articles/ibm-lawsuit-zurich-startup-lzlabs); [The Register, March 2022](https://www.theregister.com/2022/03/22/ibm_lzlabs_lawsuit/)
- A central issue was *"whether the defendants are entitled to rely on rights of observation, studying and testing and/or interoperability, conferred by Directive 2009/24/EC ('the Software Directive'), implemented by the Copyright, Designs and Patents Act 1988"* — [4 Pump Court case note](https://www.4pumpcourt.com/judgment-handed-down-in-ibm-united-kingdom-ltd-v-lzlabs-gmbh-ors-2025-ewhc-532-tcc/)
- **The court rejected those defences.** It rejected Winsopia's argument that its conduct was permitted as *"observation, study and testing"* or as *"necessary to achieve interoperability of customer applications"* — [Brick Court Chambers: Court finds conspiracy to reverse engineer IBM mainframe software](https://www.brickcourt.co.uk/news/detail/court-finds-conspiracy-to-reverse-engineer-ibm-mainframe-software)
- Winsopia was found to have breached its IBM Customer Agreement (ICA) through *"reverse-engineering and disassembly of IBM's mainframe software"*, deploying *"a number of invasive reverse engineering techniques, including disassembly, decompilation and translation, on a large scale over a period of several years"*; LzLabs GmbH and Mr Moores were liable for **procuring** those breaches — [Brick Court Chambers](https://www.brickcourt.co.uk/news/detail/court-finds-conspiracy-to-reverse-engineer-ibm-mainframe-software); [SCL: TCC upholds IBM's claim for breach of software licence by reverse engineering](https://www.scl.org/tcc-upholds-ibms-claim-for-breach-of-software-licence-by-reverse-engineering/)
- The breaches' *"nature and extent, and the duration over which they occurred, were indicative of deliberate and systematic disregard of the terms of the ICA"*; because they were concealed from IBM UK, the defendants could not rely on contractual or statutory **limitation** defences — [Brick Court Chambers](https://www.brickcourt.co.uk/news/detail/court-finds-conspiracy-to-reverse-engineer-ibm-mainframe-software)
- The court found an **unlawful means conspiracy** and **rejected reliance on the defendants' "clean room" procedures**, which were *"ostensibly designed to maintain operational separation"* — [Brick Court Chambers](https://www.brickcourt.co.uk/news/detail/court-finds-conspiracy-to-reverse-engineer-ibm-mainframe-software)
- Full judgment text: [IBM UK Ltd v LzLabs GmbH & Ors [2025] EWHC 532 (TCC), National Archives Caselaw](https://caselaw.nationalarchives.gov.uk/ewhc/tcc/2025/532). Earlier interlocutory judgments: [[2023] EWHC 3015](https://caselaw.nationalarchives.gov.uk/ewhc/tcc/2023/3015), [[2023] EWHC 2072](https://caselaw.nationalarchives.gov.uk/ewhc/tcc/2023/2072), [[2023] EWHC 2142](https://caselaw.nationalarchives.gov.uk/ewhc/tcc/2023/2142). A Court of Appeal decision exists at [LZLabs GmbH & Ors v IBM UK Ltd [2025] EWCA Civ 842](https://caselaw.nationalarchives.gov.uk/ewca/civ/2025/842) — **its holding was not verified.**
- A parallel **Texas** suit alleges patent infringement; LzLabs has argued publicly that its product was built lawfully under EU and UK software law — [Sifted](https://sifted.eu/articles/ibm-lawsuit-zurich-startup-lzlabs); [ZDNet Australia](https://www.zdnet.com.au/article/ibm-launches-lawsuit-against-lzlabs-in-ip-battle/)
- Analysts have framed the case as *"a cautionary tale for IT buyers"* — [TechTarget](https://www.techtarget.com/it-infrastructure/news/366620383/Analysts-IBM-LzLabs-suit-a-cautionary-tale-for-IT-buyers)

**Other analogous disputes:**
- **IBM v. Micro Focus (US, filed November 2022)** — IBM alleges Micro Focus used developer access to reverse engineer **CICS** to build a competing enterprise server; claims include copyright infringement and breach of contract, seeking damages and an injunction — [The Register, 22 Nov 2022](https://www.theregister.com/2022/11/22/ibm_sues_micro_focus_for/)
- **CA v. ISI Software (2010)** — CA sued over a **migration tool** that moved customers off CA's Datacom database, alleging unauthorized reproduction of source and object code — [Database Journal](https://www.databasejournal.com/database-news/ca-sues-software-developer-isi-software-over-db2-migration-tool/)
- **SAS Institute v. World Programming** — the clearest demonstration of the EU/US split: WPL won on EU copyright (CJEU C-406/10, 2012; UK final judgment 2013) yet was held liable in the US for **breach of the licence agreement** — [CMS Law](https://cms.law/en/gbr/legal-updates/sas-v-wpl-who-dares-loses); [4th Cir. opinion](https://eff.org/files/2021/10/14/sas_v._wpl_ca4-opinion_10-24-2017.pdf)

### Inferences
- **The pattern across all four disputes is the same, and it is the single most useful risk signal in this research:** the vendor's winning claim is **breach of contract**, not copyright infringement. Copyright defences (fair use, Art. 5(3)/6) are narrow, fact-intensive and were defeated or sidestepped; the licence clause did the work. For an OutSystems migration project this means MSA §3.2 is the operative risk, not the Copyright Act.
- **What distinguished the losing defendants from a legitimate internal migration** is instructive and directly actionable: all involved (a) building a **commercial product that competed with the licensor**, (b) **large-scale, prolonged, invasive** decompilation of the vendor's own software, (c) **concealment** from the licensor, and (d) in LzLabs, use of a licensee entity as a conduit for a non-licensee developer. A customer extracting its own application's logic, from artefacts it owns, for its own internal migration, documented and disclosed, sits on the opposite side of every one of those factors.
- **The "clean room" finding is a warning worth surfacing prominently:** LzLabs' clean-room separation was rejected as *"ostensibly designed to maintain operational separation"*. Procedural theatre does not cure a contractual breach, and organisations should not treat a clean room as a substitute for either authorisation or genuine minimisation.
- **Restriction (v) of MSA §3.2 is the clause that converts a low-risk project into an LzLabs-shaped one.** The moment extraction tooling is productised, resold, or used to build an OutSystems-compatible runtime, the "competitive product" prohibition — and the Art. 6(2) "substantially similar in its expression" bar — come into play.
- The absence of low-code precedent most likely reflects market youth and the fact that disputes settle quietly, **not** vendor tolerance. It should not be read as comfort.

### Gaps
- **No OutSystems litigation of any kind over reverse engineering or migration was located.** Searches covered OutSystems directly and comparable vendors (Mendix, Salesforce, ServiceNow, Appian) — nothing found. I did not search national court dockets (PACER, Portuguese or Dutch registries) and cannot exclude unreported or settled matters.
- The LzLabs **Court of Appeal** outcome ([2025] EWCA Civ 842) and the quantum/injunction hearing result are **unverified** — the report should either read those judgments or state the position as of the March 2025 liability judgment only.
- The detailed *reasoning* by which O'Farrell J rejected the Art. 5(3) and Art. 6 defences could not be retrieved: the SCL and 4 Pump Court case notes both returned **HTTP 403**. Only the outcome, via Brick Court Chambers, is sourced. The primary judgment at caselaw.nationalarchives.gov.uk should be read directly for the Software Directive analysis — this is the most valuable unread source in this research.
- The IBM v Micro Focus outcome (settled? pending?) was not determined.

---

## Q7. Practical risk guidance — staying clearly on the right side

### Takeaway
The dominant risk is **contractual, not copyright**, and it is largely controllable by project design: use the vendor-sanctioned Detachment and documented APIs first; keep extraction confined to artefacts you own; never touch platform binaries; keep the output internal; and get it in writing.

### Cited Findings supporting each measure
- **Use the contractual exit right.** MSA §8.4(ii) grants Detachment of Applications *"in source code format"* plus Customer Content, on written notice, with fees paid, **within 30 days following the end of the Subscription Term** — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/). Because the standard MSA grants **no in-term export right**, an in-term portability right must be negotiated into the Order.
- **Check the actual signed contract and its governing law.** OutSystems maintains a separate page on the contracting entity, governing law and jurisdiction — [OutSystems: Contracting company, governing law and jurisdiction](https://www.outsystems.com/legal/governing-law-jurisdiction). The published MSA is standard-form and *"Updated: February 1, 2026"*; an existing customer may be on an earlier version or a negotiated variant — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/)
- **The statutory exceptions require minimisation.** EU Art. 6 requires that acts be *"confined to the parts of the original program which are necessary"* and that the information *"has not previously been readily available"* — [Directive 2009/24/EC Art. 6](https://www.legislation.gov.uk/eudr/2009/24/article/6). US §1201(f)(1) permits circumvention only for *"the sole purpose of identifying and analyzing those elements of the program"* necessary for interoperability — [17 U.S.C. §1201](https://www.law.cornell.edu/uscode/text/17/1201). Atari: copying beyond what is necessary is infringement — [Duke IP materials](https://courses.cs.duke.edu/cps182s/fall02/cscopyright/Copyrights/Copyright-Fairuse.htm)
- **Keep output internal.** Art. 6(2) bars passing information to others except where necessary for interoperability, and bars use for a *"substantially similar"* program — [Directive 2009/24/EC Art. 6(2)](https://www.legislation.gov.uk/eudr/2009/24/article/6/data.html). §1201(f)(3) permits sharing *"solely for the purpose of enabling interoperability"* — [17 U.S.C. §1201](https://www.law.cornell.edu/uscode/text/17/1201). MSA §3.2(v) bars use *"for the purpose of building or operating a competitive product"* and §3.2(vi) bars disclosing benchmark results — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/)
- **Don't defeat technical controls.** MSA §3.2(iv) bars circumventing access or usage-measurement controls — [OutSystems MSA](https://www.outsystems.com/legal/master-subscription-agreement/); §1201(a)(1)(A): *"No person shall circumvent a technological measure that effectively controls access to a work protected under this title."* — [17 U.S.C. §1201](https://www.law.cornell.edu/uscode/text/17/1201)
- **Don't conceal, and don't rely on clean rooms as a fix.** Concealment cost the LzLabs defendants their limitation defences, and their clean-room procedures were rejected — [Brick Court Chambers](https://www.brickcourt.co.uk/news/detail/court-finds-conspiracy-to-reverse-engineer-ibm-mainframe-software)
- **Documented, supported routes exist and should be exhausted first**: the ODC Portal Subscription Console for usage data — [ODC and O11 Fair Usage Limits](https://www.outsystems.com/legal/fair-use-limits); and a BSD-3-licensed community Forge asset for module source download for SAST — [SourceCode Download O11](https://www.outsystems.com/forge/component-overview/20411/sourcecode-download-o11). Forum guidance for cloud-hosted environments is to obtain database and machine configuration details from OutSystems support rather than self-serve — [OutSystems Forum](https://www.outsystems.com/forums/discussion/45764/outsystems-export-source-code-for-code-scanning)
- **Third parties are inside the perimeter**: EULA §3.2 binds the customer not to *"allow any third party to"* do the restricted acts — [OutSystems EULA](https://www.outsystems.com/legal/end-user-licensing-agreement/)

### Inferences — a practical checklist (interpretation, not advice)
**Do, in roughly this order:**
1. **Read the actual signed Order and MSA version**, and identify the contracting OutSystems entity and governing law. EU/UK law gives mandatory, non-waivable exceptions; US law does not. This single fact changes the risk profile.
2. **Ask OutSystems for exit assistance in writing** — Detachment scope, what the package contains, whether runtime DLLs are included and under what licence, and the ODC equivalent. Written vendor consent or a documented process removes the contractual question entirely, which is where the actual litigation risk lives. There is no downside to asking.
3. **Exhaust documented and supported routes first**: Detachment output, LifeTime/ODC APIs, the metadata database, Forge SAST export, documented REST/SOAP interfaces. This both reduces work and, if decompilation is later needed, builds the record that the information "was not previously readily available".
4. **Scope extraction to what you own**: your Application's logic, entities, screens, queries, and your Customer Content. Record *interface shapes* you must call; do not carry vendor implementation code into migrated output.
5. **Hard exclusion list**: Platform Server, Service Studio, Integration Studio, LifeTime, Deployment Controller, licence-enforcement components, and `OutSystems.*` runtime assemblies. Do not decompile them; do not bypass any protection on them.
6. **Minimise and log.** Decompile the least necessary, stop when you have the information, and keep a contemporaneous record of what was accessed, why, and which cheaper route was tried first. Both Art. 6 and §1201(f) turn on necessity, and the LzLabs findings on scale and duration show how an audit trail cuts both ways — but concealment is worse than disclosure.
7. **Keep the toolkit internal and non-distributable** during the migration. Publishing a general-purpose OML parser or an OutSystems-compatible runtime is the step that converts this from a §117/Art. 5(3) story into an LzLabs/§3.2(v) story. If distribution is wanted later, take separate advice.
8. **Involve legal and procurement before building, not after.** Raise it during a renewal negotiation, where there is leverage to add an explicit in-term extraction right and an acknowledgement that the customer may parse its own OML.
9. **Avoid framing the project as competitive**. Internal documentation and one-time migration of your own estate is a different legal object from a product; project naming, README language and commit messages will be read as evidence if a dispute ever arises.

### Gaps
- No OutSystems-published guidance on acceptable third-party analysis of customer applications was found, so there is no vendor-sanctioned safe harbour to point to beyond Detachment.
- Whether OutSystems in practice grants written permission for customer-driven extraction is unknown — no public examples found.
- Insurance/indemnity angles (whether E&O or cyber policies respond to a licence-breach claim) were not researched.

---

## Cross-cutting caveats for the report writer

1. **Quotation fidelity.** Several passages above are close paraphrase, not verbatim, because the fetch tool caps quotations at ~125 characters: MSA §3.2(i)–(xi), MSA §8.4, and 17 U.S.C. §1201(f)(1)–(3). These are explicitly flagged at the point of use. **Do not present them in the final report inside quotation marks** without re-reading the source.
2. **Two sources could not be read at all** and their content is not represented here: the official OutSystems O11 detach documentation (HTTP 404 at `success.outsystems.com/support/licensing/detach_process_for_outsystems_11/`), and the SCL / 4 Pump Court case notes on LzLabs (HTTP 403). The LzLabs Software Directive *reasoning* is therefore sourced only to a chambers summary.
3. **The strongest single unread source** is the primary judgment: [IBM UK Ltd v LzLabs GmbH [2025] EWHC 532 (TCC)](https://caselaw.nationalarchives.gov.uk/ewhc/tcc/2025/532). Its Software Directive analysis is the most directly relevant authority found in this research and should be read before the report makes claims about how Art. 5(3)/Art. 6 defences fare in practice.
4. **One third-party source should be excluded entirely.** A page at `kamupi.poliupg.ac.id` purports to summarise the "OutSystems Master Subscription Agreement" but is not an OutSystems document and its structure does not match the real MSA. It appeared in multiple search results and must not be cited.
5. **Jurisdictional scope.** This covers EU/UK and US only. Other jurisdictions differ substantially — some have narrower reverse-engineering exceptions and no mandatory anti-override rule — and the report should say so rather than generalise.
6. **Headline framing suggestion.** The accurate, non-alarmist and non-dismissive summary is: *extracting your own application's logic and data from packages you own is well supported by the ownership terms OutSystems itself wrote (MSA §6) and by statute; decompiling OutSystems's platform software is contractually prohibited and only narrowly excused by statute; the OML format sits in a genuinely contested middle because OutSystems defines it as its own "Software"; and the realistic exposure is a breach-of-contract claim, which is exactly the claim that succeeded in every analogous dispute found.*
