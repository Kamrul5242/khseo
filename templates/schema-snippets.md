# Structured-data snippets (JSON-LD)

Rules: fill only with values that are visible on the page and true. Remove any property you
can't fill. One source of truth — don't let a theme and a plugin both emit Product. Escape `<`
as `<` when injecting via JS. Validate with Google's Rich Results Test / Schema.org
validator (or `scripts/seo_probe.py`, which at least checks the JSON parses).

## Organization + WebSite (site-wide, usually on the homepage)
```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#org",
      "name": "Example Brand",
      "url": "https://example.com/",
      "logo": "https://example.com/logo.png",
      "sameAs": ["https://www.facebook.com/example", "https://www.instagram.com/example"],
      "contactPoint": {"@type": "ContactPoint", "contactType": "customer support", "email": "support@example.com"}
    },
    {
      "@type": "WebSite",
      "@id": "https://example.com/#website",
      "url": "https://example.com/",
      "name": "Example Brand",
      "publisher": {"@id": "https://example.com/#org"}
    }
  ]
}
```

## Product + Offer (+ rating only if genuine reviews are shown on the page)
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Classic Cotton Tee",
  "image": ["https://example.com/img/tee-front.jpg"],
  "description": "Heavyweight 220 gsm cotton t-shirt with a relaxed fit.",
  "sku": "TEE-001",
  "brand": {"@type": "Brand", "name": "Example Brand"},
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/products/classic-cotton-tee",
    "priceCurrency": "USD",
    "price": "24.00",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition"
  }
}
```

## BreadcrumbList
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/"},
    {"@type": "ListItem", "position": 2, "name": "T-Shirts", "item": "https://example.com/t-shirts"},
    {"@type": "ListItem", "position": 3, "name": "Classic Cotton Tee"}
  ]
}
```

## BlogPosting
```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "How to Choose a T-Shirt Fabric",
  "datePublished": "2026-01-10",
  "dateModified": "2026-03-02",
  "author": {"@type": "Person", "name": "Real Author Name", "url": "https://example.com/about/author"},
  "publisher": {"@id": "https://example.com/#org"},
  "image": "https://example.com/img/fabric-guide.jpg",
  "mainEntityOfPage": "https://example.com/blog/tshirt-fabric-guide"
}
```

## LocalBusiness
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Example Bakery",
  "address": {"@type": "PostalAddress", "streetAddress": "12 Main St", "addressLocality": "Dhaka", "addressCountry": "BD"},
  "telephone": "+880-0000-000000",
  "openingHours": "Mo-Sa 08:00-20:00",
  "url": "https://example.com/"
}
```

## FAQPage (only when the Q&A is visible on the page)
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "Do you ship internationally?",
    "acceptedAnswer": {"@type": "Answer", "text": "Yes, to 30 countries. Delivery takes 7–14 business days."}
  }]
}
```
