# KFC India legal and footer capture

Captured from the official KFC India offers page on 2026-08-12.

Source page: <https://online.kfc.co.in/offers>

## Footer categories observed

### Legal

- Terms and Conditions: <https://online.kfc.co.in/terms-and-conditions>
- Privacy Center: <https://privacy.kfc.co.in/policies>
- Disclaimer: <https://online.kfc.co.in/about-kfc/disclaimer>
- Caution Notice: <https://online.kfc.co.in/about-kfc/caution-notice>

### KFC India

- About KFC: <https://online.kfc.co.in/about-kfc>
- KFC Care: <https://online.kfc.co.in/about-kfc/kfc-care>
- Careers: <https://online.kfc.co.in/about-kfc/careers>
- Our Golden Past: <https://online.kfc.co.in/about-kfc/our-golden-past>
- Responsible Disclosure: <https://bugcrowd.com/a19f4258-c79b-4a4f-a8bc-d924f85d5c53/external/report>

### KFC Food

- Menu: <https://online.kfc.co.in/menu>
- Order Lookup: <https://online.kfc.co.in/>
- Gift Card: <https://online.kfc.co.in/giftcards>
- Nutrition and Allergen: <https://online.kfc.co.in/about-kfc/nutrition>

### Support

- Get Help: <https://online.kfc.co.in/help>
- Contact Us: <https://online.kfc.co.in/contactus>
- KFC Feedback: <https://feedback.kfcIndia.co.in>
- Find a KFC: <https://restaurants.kfc.co.in/>

## Legal-page content captured

### Terms and Conditions

The page contains sections titled:

1. General Terms and Conditions
2. Home Delivery Terms and Conditions
3. KFC Rewards/Offers Terms and Conditions
4. Offers Terms and Conditions
5. Disclaimer
6. Paytm UPI Cashback Offer

The opening notice states that using the website, mobile site, or app constitutes agreement to the published terms and incorporated terms. Store the page as a legal reference document, but do not treat it as product, price, or offer data.

### Disclaimer

The page states that KFC India aims to keep site information accurate but does not warrant that the site is error-free or continuously current. It also describes limitations of liability, product/service availability language, changes to site information, trademark ownership, and a food-related caution notice.

### Caution Notice

The page warns users about fraudulent websites, messaging groups, franchise solicitations, remote-job offers, and unauthorized emails misusing the KFC name. It identifies the official KFC India website and provides a grievance-reporting contact.

### Nutrition and Allergen

The footer links to the official nutrition and allergen page. The page did not expose readable nutrition text during this capture, so the existing nutrition booklet remains a separate source requiring validation.

## RAG classification

Keep these as a separate `legal_and_policy` collection. Do not mix them with product, nutrition, or offer records. Every legal document should carry:

```text
source_url
page_title
captured_at
document_type
section_name
verification_status
```

Offer records belong in the `offers` table and should use the explicit validity dates captured from the offer detail panels. Offers without an explicit end date should remain date-unknown and should not be described by the chatbot as permanently valid.
