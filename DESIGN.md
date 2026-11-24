# DESIGN.md: UI/UX standard for the RehabGraph-RAG frontend

> This document is the **single shared source** for the UI. Anyone coding the frontend reads this file first, then `FRONT-END-ARCHITECTURE.md` and `AGENTS.md`.
>
> Updated: 25/11/2026.
>
> Note: the app UI is in Vietnamese. When this document quotes UI text, the Vietnamese text is kept, with the English meaning in brackets.

---

## 0. Sources and status

| Item | Content |
|---|---|
| Figma file | https://www.figma.com/design/kDyzPszBsKdLgkG7IrilSW/Untitled?node-id=2-3 |
| What is in Figma | **Only 1 page**: Landing Page (home page for guests), 1440px wide. |
| How it was made | The page was imported from HTML with the *html.to.design* plugin. So Figma has **no** Variables, Styles, or Components. Every value below was **read directly from each layer**. |
| Not in Figma yet | Login screen, role workspaces, AI chat panel, tables, business forms, error / empty / loading states, phone screens, dark mode. See **section 10**. |

Labels used in this file:

- ✅ **From Figma**: the value is taken exactly from Figma.
- 💡 **Proposal**: not in Figma, this is a suggestion. The team needs to approve it.
- ⛔ **MISSING**: not in Figma and no proposal yet. The designer needs to add it.

---

## 1. General principles

1. **One source of tokens.** Colors, fonts, and radius are only declared in `src/index.css` (CSS variables) and the Tailwind theme. Never hard-code a color (`#F4A98C`) in a component.
2. **Use shadcn/ui first.** For Button, Input, Dialog, Table... take them from `shared/ui` (shadcn/ui). Only write your own when shadcn does not have it.
3. **Simple, easy-to-read text.** Users include older patients and relatives. Short sentences, large enough font, contrast that meets the standard (section 11).
4. **No hard-coded text.** All text goes through i18next (`vi.json`), as in `FRONT-END-ARCHITECTURE.md`.
5. **AI answers always show their source.** Anywhere an AI answer is shown, the Ministry of Health (MoH) document citation must be shown too.

---

## 2. Colors

### 2.1. Base palette (✅ From Figma)

Figma style: **dark moss green + peach**, light cream background.

| Token name | Color | Where it is used in Figma |
|---|---|---|
| `teal-900` | `#0F3B38` | Background of header, hero, footer, CTA strip. Heading color on light backgrounds. Dark buttons. |
| `teal-800` | `#174844` | Background of the "features" block next to the CTA, contact form background. |
| `teal-700` | `#2A5A56` | Secondary illustration frame in the hero. |
| `teal-500` | `#4D7A76` | Inactive carousel dot. |
| `teal-100` | `#CFE3DF` | Avatar background, article image background. |
| `peach-400` | `#F4A98C` | **Main accent color**: main buttons, round icons, highlighted text, menu text, ★ stars, feature card footer. |
| `cream-50` | `#FDF1EC` | Background of light sections, background of round icons in cards. |
| `border-warm` | `#F1DDD4` | Card border. |
| `border-warm-2` | `#EADFD9` | Divider lines between FAQ questions. |
| `white` | `#FFFFFF` | Card background, input background, text on dark backgrounds. |

**Text colors (✅ From Figma):**

| Token name | Color | Where it is used |
|---|---|---|
| `text-strong` | `#0F3B38` | Headings, main text on light backgrounds. |
| `text-muted` | `#5D7472` | Descriptions, meta (e.g. "Cơ xương khớp · 5 phút đọc" [Musculoskeletal · 5 min read]). |
| `text-placeholder` | `#8AA09D` | Input placeholder. ⚠️ Fails contrast, see section 11. |
| `text-on-dark` | `#FFFFFF` | Headings on dark backgrounds. |
| `text-on-dark-muted` | `#A9C3BF` | Descriptions on dark backgrounds. |
| `text-accent` | `#F4A98C` | Highlighted text, eyebrow, the "Đọc tiếp →" [Read more →] link. |

> Figma also has many skin and hair colors in the doctor illustration (`#E5AC8C`, `#3A2A24`...). Those belong to the drawing, **not UI tokens**, and do not go into the theme.

### 2.2. Status colors

| Status | Value |
|---|---|
| Error / danger (`destructive`) | ⛔ MISSING |
| Success (`success`) | ⛔ MISSING |
| Warning (`warning`) | ⛔ MISSING. Badly needed for "Safety warning" (signs to stop exercising). |
| Info (`info`) | ⛔ MISSING |

Until they exist, use the shadcn default color for `destructive` and add the note `// TODO: waiting for Figma`.

### 2.3. Mapping to the shadcn/ui theme (💡 Proposal)

shadcn names tokens by **role** (primary, muted...). The table below assigns Figma colors to each role:

| shadcn token | Color | Reason |
|---|---|---|
| `--background` | `#FFFFFF` | The app background inside workspaces should be white so tables and forms are easy to read. |
| `--foreground` | `#0F3B38` | Main text. |
| `--primary` | `#0F3B38` | Main button in the app (dark button, white text). Contrast 12.3:1. |
| `--primary-foreground` | `#FFFFFF` | |
| `--accent` | `#F4A98C` | Emphasis button (CTA), highlights. Text on it must be `#0F3B38`. |
| `--accent-foreground` | `#0F3B38` | |
| `--secondary` | `#FDF1EC` | Secondary buttons, light block backgrounds. |
| `--secondary-foreground` | `#0F3B38` | |
| `--muted` | `#FDF1EC` | Background of secondary areas. |
| `--muted-foreground` | `#5D7472` | Secondary text. |
| `--card` | `#FFFFFF` | |
| `--card-foreground` | `#0F3B38` | |
| `--popover` / `--popover-foreground` | `#FFFFFF` / `#0F3B38` | |
| `--border` | `#F1DDD4` | Card border in Figma. |
| `--input` | `#F1DDD4` | 💡 Figma only has inputs on dark backgrounds (no border). On white they need a border, so we use the card border color for now. |
| `--ring` | `#0F3B38` | 💡 Focus ring. Not in Figma. |
| `--destructive` | ⛔ MISSING | |
| `--sidebar` | `#0F3B38` | 💡 The workspace menu bar uses the Figma header color. |
| `--sidebar-foreground` | `#A9C3BF` | |
| `--sidebar-primary` | `#F4A98C` | Selected menu item. |
| `--sidebar-primary-foreground` | `#0F3B38` | |

> In Figma, the landing page uses the **peach button** as the main button. For the internal app, we propose the **dark green button as the main button** and keep peach for the single most important action on a page (e.g. "Gửi câu hỏi" [Send question], "Duyệt lộ trình" [Approve pathway]). Reason: many peach buttons on a table screen look messy. The team can decide otherwise.

---

## 3. Typography

### 3.1. Font (✅ From Figma)

- **Be Vietnam Pro** for the whole UI. This font supports Vietnamese diacritics very well.
- Weights used: **Regular 400**, **Medium 500**, **Bold 700**.
- Load from Google Fonts or the `@fontsource/be-vietnam-pro` package (💡 we propose the npm package so the app does not depend on an outside network, because it runs inside the center).
- Fallback font: `system-ui, sans-serif`.

### 3.2. Font size scale (✅ From Figma)

| Token | Size / line height | Weight | Where it is used in Figma |
|---|---|---|---|
| `display` | 58 / 66.7px (1.15) | Bold | Hero H1. |
| `h2` | 40 / 48px (1.2) | Bold | Section headings. |
| `h2-sm` | 32 / 38.4px (1.2) | Bold | CTA strip heading. |
| `h3-lg` | 24 / 31.2px (1.3) | Bold | CTA card heading. |
| `logo` | 22px | Bold | Logo text "RehabRAG". |
| `h3` | 18px (auto) | Bold | Card, step, and article headings. |
| `title-sm` | 16px | Bold / Medium | FAQ questions (Bold), checkmark list lines (Medium). |
| `body` | 15 / 26.3px (1.75) | Regular | Main paragraphs. Header menu. |
| `body-sm` | 14 / 24.5px (1.75) | Regular | Card descriptions, input text. |
| `button` | 14px | Bold | Button text. |
| `caption` | 13px | Regular | Meta, roles, copyright. |
| `eyebrow` | 12px, uppercase, 3% letter spacing | Bold | Small line above a heading ("TÍNH NĂNG" [FEATURES]). Color `peach-400`. |
| `stat` | 28px | Bold | Big numbers ("24/7"). |

Heading style in Figma: **Capital Letter At The Start Of Each Word**, ending with a period ("Chúng Tôi Mang Đến Những Gì Tốt Nhất." [We Bring You The Best.]). Part of the heading is colored `peach-400` for emphasis.

### 3.3. Use inside the app (💡 Proposal)

The scale above is for the landing page and is quite large. Inside workspaces (tables, forms):

- Body text at least **14px**. For patient and relative screens, use **16px**.
- Page titles in workspaces: `h3-lg` (24px). Do not use `display` in the app.
- Keep paragraph line height at **1.75** like Figma, for easy reading.

---

## 4. Spacing and layout

### 4.1. Page layout (✅ From Figma)

| Item | Value |
|---|---|
| Design frame | 1440px |
| Content container | **1200px**, centered, 120px margin on each side |
| Section padding (top/bottom) | 100px (normal section), 90px, 70/120px (hero), 44px (CTA strip) |
| 3-column card grid | 3 × ~384px, 24px gap (article cards, testimonials) |
| Feature grid | 3 columns × 257px, 20px gap |
| Header height | 89px, 22px padding top/bottom |

### 4.2. Spacing scale (✅ From Figma, rounded)

Common gaps: **8, 12, 14, 16, 18, 20, 24, 26, 30, 34, 36, 40, 56, 60, 80, 90, 100px**.

💡 Proposal: **use the default Tailwind scale (multiples of 4px)**, rounding the odd Figma numbers:

| Figma | Tailwind | px |
|---|---|---|
| 8 | `2` | 8 |
| 12, 13, 14 | `3` | 12 |
| 15, 16, 18 | `4` | 16 |
| 20, 22 | `5` | 20 |
| 24, 26 | `6` | 24 |
| 30, 34, 36 | `8` / `9` | 32 / 36 |
| 40 | `10` | 40 |
| 56, 60 | `14` / `15` | 56 / 60 |
| 100 | `25` | 100 |

Reason: odd numbers like 13, 26, 34 come from the original HTML, not from design intent. Rounding keeps the code clean and looks almost the same.

### 4.3. Workspace layout

⛔ MISSING in Figma. 💡 Temporary proposal, matching `WorkspaceLayout.tsx`:

```
┌──────────────┬──────────────────────────────────────────┐
│  Sidebar     │  Topbar: page name · workspace switch ·   │
│  (teal-900)  │          user name                         │
│  logo        ├──────────────────────────────────────────┤
│  menu by     │                                            │
│  role        │  Content (white background, max-w 1200px)  │
│              │                                            │
│  240px       │                                            │
└──────────────┴──────────────────────────────────────────┘
```

- Sidebar 240px wide, color `teal-900`, selected item has a `peach-400` background with `teal-900` text (like the Figma button).
- On screens smaller than 1024px: the sidebar collapses into a menu opened by a button (shadcn `Sheet`).

---

## 5. Radius

| Token | Value | Where it is used (✅ From Figma) |
|---|---|---|
| `radius-sm` | **4px** | Buttons, inputs, textareas, carousel dots. |
| `radius-none` | 0 | **Cards have no rounded corners**: feature cards, article cards, testimonial cards, CTA block. |
| `radius-full` | 9999px | Round icons (22, 52, 64, 70, 96px), avatars. |
| Arch | `rounded-t-full` | Doctor illustration frame in the hero (top half rounded). |

💡 In shadcn, set `--radius: 4px`. The shadcn Card is rounded by default: **change Card to `rounded-none`** to match Figma.

---

## 6. Shadows

✅ Figma **does not use shadows** anywhere. Layers are separated by **background color** and a **1px `#F1DDD4` border**.

💡 Proposal: keep the flat style. Only use shadows for things that float above the page (Dialog, Popover, Dropdown), with the default Tailwind `shadow-md`. ⛔ Figma has no design for these yet.

---

## 7. Borders

| Where | Value (✅ From Figma) |
|---|---|
| Card border | 1px `#F1DDD4` |
| FAQ divider | 1px bottom, `#EADFD9` |
| Header bottom line (dark background) | 1px bottom, white 10% |
| Footer top line (dark background) | 1px top, white 12% |

---

## 8. Icons

- ✅ Icons in Figma are thin outline icons (chat, heart, activity, user, shield). They look like the **Lucide** set, which shadcn/ui already uses through `lucide-react`. 💡 Use `lucide-react` for the whole app.
- Icon sizes (✅ From Figma):

| Place | Icon | Background circle |
|---|---|---|
| Checkmark in lists | 12px | 22px, `peach-400` background |
| Feature card | 24px | 52px, `cream-50` background (on white) or `peach-400` (on dark) |
| CTA strip | 30px | 64px, `peach-400` background |
| "Cách hoạt động" [How it works] steps | 44px | 96px, white background |

- Icon color: `teal-900` on light backgrounds.

---

## 9. Components (✅ From Figma)

Each component lists: shape, size, colors, and the matching shadcn/ui name.

### 9.1. Button

| Variant | Background | Text | Where it is used | shadcn |
|---|---|---|---|---|
| **Accent** (peach button) | `#F4A98C` | `#0F3B38`, Bold 14 | "Dùng thử ngay" [Try now], "Tìm hiểu thêm →" [Learn more →], "Gửi" [Send] | `variant="accent"` (💡 new) |
| **Primary** (dark button) | `#0F3B38` | `#FFFFFF`, Bold 14 | "Xem tất cả" [See all], "Hỏi RehabRAG ngay" [Ask RehabRAG now] | `variant="default"` |
| **Ghost with icon** | no background | `#FFFFFF`, Bold 16 | "▶ Xem video giới thiệu" [Watch intro video] (46px round icon) | `variant="ghost"` |
| **Link** | no background | `#F4A98C`, Bold 14 | "Đọc tiếp →" [Read more →] | `variant="link"` |

Common size: height **44px**, padding **13px top/bottom, 24px left/right**, radius **4px**. 💡 Map to shadcn `size="default"` = `h-11 px-6`.

Hover / focus / disabled / loading states: ⛔ MISSING. 💡 For now: hover 10% darker, focus with `ring-2 ring-ring ring-offset-2`, disabled `opacity-50`, loading shows a spinner and locks the button.

### 9.2. Input and Textarea

- White background, **no border** (because Figma places it on a dark background), 4px radius, height **48px**, padding 15px.
- Text 14px Regular. Placeholder `#8AA09D` (⚠️ needs fixing, see section 11).
- Textarea height 110px.
- Input + attached button (the "Email của bạn" [Your email] box + "Gửi" [Send] button): input rounded on the left, button rounded on the right.
- 💡 On the app's white background: add a 1px `--input` border.
- ⛔ MISSING: label, error text, error state, focus, disabled, select, checkbox, radio, date picker.

### 9.3. Card

| Type | Description |
|---|---|
| **Feature card** | White background, 1px `#F1DDD4` border, no rounded corners. 26px padding. At the top a 52px round icon, then an `h3` title, then a `body-sm` description in `text-muted`. At the bottom a **peach footer strip** 42px high with the text "Xem thêm →" [See more →]. |
| **Article card** | Same as above, with a 210px image area on top, `teal-100` background. `caption` meta ("Thần kinh · 7 phút đọc" [Neurology · 7 min read]), `h3` title, "Đọc tiếp →" [Read more →] link. |
| **Testimonial card** | White background on `teal-900`, 30px padding, 14px gap. 54px round avatar, name Bold 16, role `caption`, 40px peach quote mark, peach ★ stars. |
| **Stat card** | 120×100px, `teal-900` background, number 28px Bold white, label 13px. |
| **CTA block** | `peach-400` background, 34/36px padding, 24px heading, dark button. |

### 9.4. Accordion (FAQ)

- Each row: 1px `#EADFD9` bottom line, 18px padding top/bottom.
- Question Bold 16 `teal-900`. `+` / `−` sign in `peach-400`, size 22px, on the right.
- Answer in `body`, color `text-muted`.
- shadcn: `Accordion`. Replace the default chevron with `+` / `−` to match Figma.

### 9.5. Checkmark list

22px circle with `peach-400` background + 12px check icon, 12px from the text. Text Medium 16.

### 9.6. Carousel dots

8×8px dots, 4px radius, color `#4D7A76`. The active dot is 28px long, color `peach-400`. 8px apart.

### 9.7. Header (guest page)

`teal-900` background, 89px high. Logo (40px icon + 22px Bold text) on the left. Menu in the middle: 15px text in `peach-400`, 36px apart. Accent button on the right.

⛔ MISSING: selected / hover state for menu items.

### 9.8. Footer

`teal-900` background, 4 columns (logo + description, Links, Support, Newsletter). Column titles 18px Bold white, links 15px `#A9C3BF`. Copyright line 13px, with a white 12% line on top.

### 9.9. App components needed but missing in Figma (⛔)

These are **required** for the MVP but Figma has not drawn them. Code uses shadcn defaults + the tokens above until designs exist:

| Component | Used for | shadcn |
|---|---|---|
| **AI chat panel** | Q&A for every role | Built from `ScrollArea`, `Textarea`, `Button` |
| **Source citation** | Each AI answer points to an MoH decision (e.g. "QĐ 3554/QĐ-BYT, tr. 45" [Decision 3554, p. 45]) | `Badge` + `HoverCard` / `Sheet` to view the original passage |
| **Basic / Deep answer level switch** | Technician, doctor, curator | `ToggleGroup` |
| **Data table** | Patient list, documents, accounts | `Table` (+ TanStack Table) |
| **Business forms** | Patient record, pathway, discharge | `Form` (RHF + Zod), `Select`, `Checkbox`, `DatePicker` |
| **Confirm dialog** | Approve, reject (needs a reason) | `AlertDialog`, `Dialog` |
| **Notifications** | Saved, error | `Sonner` (toast) |
| **Status badge** | Waiting for review, approved, needs rework | `Badge` |
| **Workspace switch button** | Users with several roles | `DropdownMenu` |
| **Knowledge graph** | Cytoscape | Node / edge colors ⛔ MISSING |
| **Safety warning** | Signs to stop exercising | `Alert` with `warning` color ⛔ |
| **Empty / loading / error states** | Every list | `Skeleton` + message block |

---

## 10. What is missing in Figma (designer needs to add)

Ordered by priority for the MVP (stroke):

1. **AI chat panel + source citations + Basic / Deep switch.** This is the main feature.
2. **Workspace layout** (sidebar, topbar, workspace switch) for doctor, technician, patient, relative.
3. **Status colors**: error, success, warning, info.
4. **Component states**: hover, focus, disabled, loading, form errors.
5. **Tables and business forms.**
6. **Phone screens** (patients and relatives mostly use phones). Figma only has the 1440px version.
7. **Login, relative invite code.**
8. **Colors for the knowledge graph (Cytoscape).**
9. Dark mode: 💡 not needed for the MVP.

---

## 11. Accessibility

Goal: **WCAG 2.1 level AA**. Test with `@axe-core/playwright` as in `FRONT-END-ARCHITECTURE.md`.

### 11.1. Contrast of Figma color pairs

AA standard: normal text needs **≥ 4.5:1**, large text (≥ 18px Bold or ≥ 24px) needs **≥ 3:1**.

| Text | Background | Ratio | Result |
|---|---|---|---|
| `#0F3B38` | `#FFFFFF` | 12.3 | ✅ |
| `#0F3B38` | `#FDF1EC` | 11.1 | ✅ |
| `#0F3B38` | `#F4A98C` | 6.4 | ✅ (text on the peach button) |
| `#FFFFFF` | `#174844` | 10.3 | ✅ |
| `#A9C3BF` | `#0F3B38` | 6.6 | ✅ |
| `#F4A98C` | `#0F3B38` | 6.4 | ✅ (menu, highlighted text on dark) |
| `#5D7472` | `#FFFFFF` | 5.0 | ✅ |
| `#5D7472` | `#FDF1EC` | 4.5 | ✅ just enough |
| **`#F4A98C`** | **`#FFFFFF`** | **1.9** | ❌ **"Đọc tiếp →" [Read more →] on white cards** |
| **`#8AA09D`** | **`#FFFFFF`** | **2.8** | ❌ **Input placeholder** |

### 11.2. How to fix (💡 Proposal)

- **No peach text on white / cream backgrounds.** Change the "Đọc tiếp →" [Read more →] link on light backgrounds to `#0F3B38` with an underline, or keep peach only for the arrow icon.
- **Placeholder**: change to `#5D7472` (5.0:1). And always have a **label** above the input, do not rely on the placeholder alone.
- Use peach `#F4A98C` only as a **background** (with dark text on it) or as text on a **dark background**.

### 11.3. Other rules

- Every button and link works with the keyboard and has a clear focus ring (`ring`).
- Minimum touch target 44×44px (Figma buttons are 44px high, OK).
- Icons without text must have an `aria-label`.
- Never use **color alone** to show status. Always add text or an icon (e.g. "Chờ duyệt" [Waiting for review] + clock icon).
- Decorative illustrations: `alt=""`.

---

## 12. Writing UI text (Copy)

### 12.1. Style in Figma (✅)

- Uses "bạn" (you), friendly tone: "Đừng ngần ngại đặt câu hỏi cho chúng tôi" [Don't hesitate to ask us].
- Buttons with a clear action, with an arrow when they lead to another page: "Tìm hiểu thêm →" [Learn more →], "Đọc tiếp →" [Read more →].
- Eyebrows in uppercase, 1 to 4 words: "TÍNH NĂNG" [FEATURES], "CÁCH HOẠT ĐỘNG" [HOW IT WORKS].
- A disclaimer line: "Thông tin chỉ mang tính tham khảo, không thay thế chẩn đoán của bác sĩ." [Information is for reference only and does not replace a doctor's diagnosis.]

### 12.2. Rules for the app (💡 Proposal)

1. **Short sentences**, one idea per sentence. Avoid medical jargon when talking to patients and relatives.
2. Buttons start with a **verb**: "Lưu" [Save], "Gửi câu hỏi" [Send question], "Duyệt lộ trình" [Approve pathway]. Never use "OK".
3. Error messages say **what happened and what to do next**: "Chưa nhập lý do từ chối. Vui lòng nhập lý do." [No rejection reason entered. Please enter a reason.]
4. Titles inside the app use sentence case (not Title Case like the landing page): "Bệnh nhân của tôi" [My patients].
5. Abbreviations only for staff: BS (doctor), KTV (technician), BN (patient), PHCN (rehabilitation). For patients and relatives, write them in full.
6. Dates and times: `dd/MM/yyyy HH:mm`, Vietnam time.

### 12.3. ⚠️ Figma content does not match the project scope

The landing page text currently **does not match** decisions already made. Fix it in Figma before coding:

| In Figma | Problem | Suggestion |
|---|---|---|
| Name "RehabRAG" | The project name is **RehabGraph-RAG** | Agree on one name. |
| "Muốn Dùng RehabRAG Cho Phòng Khám?" [Want RehabRAG for your clinic?], "Làm sao để dùng cho phòng khám?" [How to use it for a clinic?], form with a "Đơn vị / Phòng khám" [Organization / Clinic] field, "Dùng thử ngay" [Try now] button | The app is the **internal system of one rehabilitation center**, not sold to other clinics | Remove the contact form and "Try now". Replace with "Đăng nhập" [Log in]. |
| "tài liệu y khoa chọn lọc" [selected medical documents], "kho tài liệu được nhóm chọn lọc" [document library selected by the team] | The source is **MoH documents** (Decisions 3553, 3554, 3555, 5623) | Say clearly "theo hướng dẫn của Bộ Y tế" [following Ministry of Health guidance]. |
| "mọi thứ diễn ra trong vài giây" [everything happens in seconds] | The project **does not promise a response time** | Remove this sentence. |
| "Hỗ trợ 24/7" [24/7 support], "Nhận bản tin" [Get the newsletter] | Not in scope | Remove, or ask the team. |
| Article examples about "đầu gối" [knee], "đau lưng" [back pain] | The MVP only covers **stroke** | Change the examples to stroke. |
| Testimonials "[Tên người dùng]" [User name] | Placeholder text | Remove from the MVP or wait for real data. |

---

## 13. Tailwind + shadcn/ui configuration

The project uses **Tailwind CSS v4** (decided, see FRONT-END-ARCHITECTURE §1), through the `@tailwindcss/vite` plugin. There is no `tailwind.config.ts`: all tokens go in `src/index.css` as below. `components.json` (shadcn) already points to `src/index.css` and puts components in `src/shared/ui`.

```css
/* src/index.css */
@import "tailwindcss";
@import "@fontsource/be-vietnam-pro/400.css";
@import "@fontsource/be-vietnam-pro/500.css";
@import "@fontsource/be-vietnam-pro/700.css";

:root {
  /* Base palette (Figma) */
  --teal-900: #0F3B38;
  --teal-800: #174844;
  --teal-700: #2A5A56;
  --teal-500: #4D7A76;
  --teal-100: #CFE3DF;
  --peach-400: #F4A98C;
  --cream-50: #FDF1EC;
  --border-warm: #F1DDD4;
  --border-warm-2: #EADFD9;
  --text-muted: #5D7472;
  --text-on-dark-muted: #A9C3BF;

  /* shadcn tokens (section 2.3) */
  --background: #FFFFFF;
  --foreground: var(--teal-900);
  --card: #FFFFFF;
  --card-foreground: var(--teal-900);
  --popover: #FFFFFF;
  --popover-foreground: var(--teal-900);
  --primary: var(--teal-900);
  --primary-foreground: #FFFFFF;
  --secondary: var(--cream-50);
  --secondary-foreground: var(--teal-900);
  --muted: var(--cream-50);
  --muted-foreground: var(--text-muted);
  --accent: var(--peach-400);
  --accent-foreground: var(--teal-900);
  --destructive: #DC2626; /* TODO: waiting for Figma. Temporary default red. */
  --border: var(--border-warm);
  --input: var(--border-warm);
  --ring: var(--teal-900);
  --radius: 4px;

  --sidebar: var(--teal-900);
  --sidebar-foreground: var(--text-on-dark-muted);
  --sidebar-primary: var(--peach-400);
  --sidebar-primary-foreground: var(--teal-900);
  --sidebar-border: rgb(255 255 255 / 0.1);
}

@theme inline {
  --font-sans: "Be Vietnam Pro", system-ui, sans-serif;

  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-sidebar: var(--sidebar);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
  --color-sidebar-border: var(--sidebar-border);

  /* Base colors, use when needed (e.g. landing section backgrounds) */
  --color-teal-900: var(--teal-900);
  --color-teal-800: var(--teal-800);
  --color-teal-700: var(--teal-700);
  --color-teal-500: var(--teal-500);
  --color-teal-100: var(--teal-100);
  --color-peach-400: var(--peach-400);
  --color-cream-50: var(--cream-50);
  --color-on-dark-muted: var(--text-on-dark-muted);

  --radius-sm: 4px;
  --radius-md: 4px;
  --radius-lg: 4px;

  /* Font scale (section 3.2) */
  --text-display: 58px;   --text-display--line-height: 1.15;
  --text-h2: 40px;        --text-h2--line-height: 1.2;
  --text-h2-sm: 32px;     --text-h2-sm--line-height: 1.2;
  --text-h3-lg: 24px;     --text-h3-lg--line-height: 1.3;
  --text-h3: 18px;        --text-h3--line-height: 1.3;
  --text-body: 15px;      --text-body--line-height: 1.75;
  --text-body-sm: 14px;   --text-body-sm--line-height: 1.75;
  --text-caption: 13px;   --text-caption--line-height: 1.4;
  --text-eyebrow: 12px;   --text-eyebrow--letter-spacing: 0.03em;

  --container-content: 1200px;
}

body {
  @apply bg-background text-foreground font-sans antialiased;
}
```

Add the `accent` button variant to `shared/ui/button.tsx` (shadcn):

```tsx
variants: {
  variant: {
    default: "bg-primary text-primary-foreground hover:bg-primary/90",
    accent:  "bg-accent text-accent-foreground hover:bg-accent/90",
    // ... keep the other shadcn variants
  },
  size: {
    default: "h-11 px-6 text-sm font-bold rounded-sm", // 44px, like Figma
    // ...
  },
}
```

Card without rounded corners (`shared/ui/card.tsx`): change `rounded-xl` to `rounded-none`, remove `shadow-sm`.

---

## 14. Decisions the team needs to make

| # | Question | Our proposal |
|---|---|---|
| 1 | Is the main app button dark green or peach? | Dark green. Peach for the 1 most important action per screen. |
| 2 | Product name: RehabRAG or RehabGraph-RAG? | Pick one, and fix Figma too. Still open (BUSINESS Q-06). Until then, code uses **RehabGraph-RAG**, and the name only lives in `vi.json` so it is easy to change. |
| 3 | Fix the landing content as in section 12.3? | Yes. |
| 4 | Who draws the screens in section 10, and when? | Do the AI chat panel + doctor / technician workspaces first. |
| 5 | Status colors (error, success, warning)? | The designer picks them and checks contrast on white. |
| 6 | Move Figma to Variables and Components? | Yes. The file is an HTML import so it has none yet. When it does, update this file with the Variable names. |

---

*When Figma changes: update this file first, then change the code.*
