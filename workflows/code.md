# Mode B — Vibe Coder / Developer

**Trigger:** a repository or project files are available, a framework is named, or the user asks
to fix/implement SEO in code. Always read [rules/governance.md](../rules/governance.md) too.

```
CAPABILITY CHECK → DETECT → AUDIT → PLAN → GATE → IMPLEMENT → TEST → VERIFY → REPORT
```

**GATE** applies the canonical risk rule in [governance.md §0](../rules/governance.md):
R0–R1 proceed, R2 is shown and waits for authorization, R3–R4 need explicit confirmation plus
a recovery point.

## 1. Detect (never assume the framework)

Read the manifest(s) and config before anything else.

| Evidence | Stack | Where SEO lives |
|---|---|---|
| `next` in package.json + `app/` dir | Next.js App Router | `export const metadata` / `generateMetadata` in `layout.tsx`/`page.tsx`; `app/sitemap.ts`, `app/robots.ts`; JSON-LD via `<script type="application/ld+json">` in the page |
| `next` + `pages/` dir | Next.js Pages Router | `next/head` per page, `_document.tsx`, `next-sitemap` config |
| `nuxt` | Nuxt 3 | `useHead` / `useSeoMeta`, `nuxt.config` `app.head`, `@nuxtjs/sitemap`, `@nuxtjs/robots` |
| `astro` | Astro | layout `<head>`, `@astrojs/sitemap`, frontmatter-driven meta |
| `@sveltejs/kit` | SvelteKit | `<svelte:head>`, `+page.ts` load data, prerender config |
| `vite` + `react` only (no SSR) | React SPA | `react-helmet-async` / React 19 `<title>` hoisting — **CSR risk: flag it** |
| `vue` + vite only | Vue SPA | `@unhead/vue` — **CSR risk** |
| `gatsby` | Gatsby | `Head` export, `gatsby-plugin-sitemap` |
| `composer.json` + `laravel/framework` | Laravel | Blade layouts `@section('title')`, `spatie/laravel-sitemap` |
| `manage.py` + Django | Django | base template blocks, `django.contrib.sitemaps` |
| `wp-content/`, `functions.php` | WordPress | theme `header.php`, Yoast/Rank Math (don't duplicate their output) |
| `.liquid` + `config/settings_schema.json` | Shopify theme | `theme.liquid` head, `{{ content_for_header }}`, product JSON-LD in `main-product.liquid` |
| Blogger XML theme (`<b:skin>`, `b:section`) | Blogger | `<b:include data='blog' name='all-head-content'/>`, conditional `<b:if cond='data:view.isPost'>` |
| only `.html` files | Static | each file's `<head>`; hand-written sitemap.xml/robots.txt |

Also record: rendering mode (SSR/SSG/ISR/CSR), i18n setup, CMS/data source, existing SEO
library, how the site is built and deployed (don't deploy — just know).

## 2. Audit the code

Search for the concrete things, not vibes:

- title/description sources — are there two competing ones?
- canonical generation — absolute? correct host? trailing-slash policy consistent with routing?
- `noindex` / `robots` usage — any env-gated noindex that leaks into production?
- sitemap generation — includes only public, canonical, 200 URLs? dynamic routes covered?
- robots.txt — generated or static? blocks assets? references sitemap?
- JSON-LD — valid JSON (no trailing commas, escaped `</script>`), data bound to real fields
- images — `alt`, width/height, `next/image`/`<picture>` usage, LCP image priority
- links — `<a href>`/`<Link>` vs `onClick` navigation; broken internal hrefs
- rendering — is product/article body in server HTML? `useEffect`-fetched content is invisible
  to non-JS crawlers
- headings — one H1 per page template
- 404/500 — real status codes, not soft 200s
- secrets — if encountered, `SECRET DETECTED` protocol; never echo values

## 3. Plan

Minimal list of changes, each tagged `P? / R?`. Show R2 items as `PROPOSED CHANGE` and group
R3/R4 into one approval request. Then apply only R0–R1 plus whatever the user authorized.
Prefer extending the existing SEO system over introducing a new library.

## 4. Implement

- Match the project's style, file layout and patterns.
- Idempotent: check the desired state doesn't already exist before adding (no duplicate schema,
  duplicate meta, duplicate sitemap entries).
- Keep the diff reviewable; no drive-by refactors.
- Content changes: preserve business facts; `[ADD: …]` placeholders instead of inventions.

## 5. Validate (only claim what you ran)

Run what exists: build, typecheck, lint, tests. Then check outputs:
- built/served HTML for 1–3 routes: title, meta description, canonical, robots meta, one H1,
  JSON-LD parses (`scripts/seo_probe.py path/to/out.html` or against a local dev server URL)
- sitemap/robots routes return the expected content
- a changed link still resolves

Anything you couldn't run → `NOT VERIFIED` with the command the user can run.

If your change broke the build and the cause is clearly your diff → revert only your diff,
re-run, report the rollback.

## 6. Report

Use [templates/code-change-report.md](../templates/code-change-report.md). Deployment is a
separate gate — never deploy because code changed.

## Framework snippets (reference, adapt to the project)

**Next.js App Router metadata**
```tsx
export async function generateMetadata({ params }): Promise<Metadata> {
  const product = await getProduct(params.slug);
  return {
    title: `${product.name} | Brand`,
    description: product.summary,
    alternates: { canonical: `https://example.com/products/${product.slug}` },
    openGraph: { title: product.name, images: [product.image] },
  };
}
```

**Next.js sitemap** (`app/sitemap.ts`)
```ts
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const products = await getPublicProducts();
  return products.map(p => ({ url: `https://example.com/products/${p.slug}`, lastModified: p.updatedAt }));
}
```

**Safe JSON-LD injection (React)**
```tsx
<script type="application/ld+json"
  dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }} />
```

**Nuxt**
```ts
useSeoMeta({ title, description, ogTitle: title, ogImage: image });
useHead({ link: [{ rel: 'canonical', href: canonicalUrl }] });
```
