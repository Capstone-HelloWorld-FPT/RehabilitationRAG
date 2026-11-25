import { useTranslation } from "react-i18next";

import { AccordionItem } from "@/shared/ui/accordion";

import team1Url from "../assets/team-1.svg";
import team2Url from "../assets/team-2.svg";
import team3Url from "../assets/team-3.svg";
import team4Url from "../assets/team-4.svg";
import { Container, Eyebrow, SectionTitle } from "./SectionText";

const faqItems = ["source", "replaceDoctor", "needLogin"] as const;

export function FaqSection() {
  const { t } = useTranslation();
  return (
    <section id="faq" aria-labelledby="faq-title" className="py-16 lg:py-27.5">
      <Container className="flex flex-col items-center gap-12 lg:flex-row lg:gap-20">
        {/* Illustration (Figma 540×420): team drawing on teal-100 + two stat cards. */}
        <div className="relative w-full max-w-135 shrink-0 pb-10">
          <div className="flex aspect-540/380 items-end bg-teal-100">
            {/* Group positions are the Figma insets inside the 540×300 drawing. */}
            <div aria-hidden="true" className="relative aspect-540/300 w-full overflow-hidden">
              <img
                src={team1Url}
                alt=""
                className="absolute top-[54%] left-[4.86%] h-[46%] w-[23.61%]"
              />
              <img
                src={team2Url}
                alt=""
                className="absolute top-[48.18%] left-[27.33%] h-[51.52%] w-[26.45%]"
              />
              <img
                src={team3Url}
                alt=""
                className="absolute top-[50.12%] left-[50.86%] h-[49.68%] w-[25.5%]"
              />
              <img
                src={team4Url}
                alt=""
                className="absolute top-[54.97%] left-[72.88%] h-[45.08%] w-[23.13%]"
              />
            </div>
          </div>
          <dl className="absolute bottom-0 left-4 flex sm:left-7.5">
            <div className="flex h-25 w-30 flex-col-reverse items-center justify-center bg-teal-900 text-white">
              <dt className="text-caption">{t("landing.faq.stats.sourceLabel")}</dt>
              <dd className="text-stat font-bold">{t("landing.faq.stats.sourceValue")}</dd>
            </div>
            <div className="bg-peach-400 flex h-25 w-30 flex-col-reverse items-center justify-center text-teal-900">
              <dt className="text-caption">{t("landing.faq.stats.languageLabel")}</dt>
              <dd className="text-stat font-bold">{t("landing.faq.stats.languageValue")}</dd>
            </div>
          </dl>
        </div>

        <div className="flex w-full flex-1 flex-col">
          <Eyebrow>{t("landing.faq.eyebrow")}</Eyebrow>
          <SectionTitle id="faq-title" className="pt-4 pb-6.5">
            {t("landing.faq.title")}
          </SectionTitle>
          {faqItems.map((item, index) => (
            <AccordionItem
              key={item}
              defaultOpen={index === 0}
              question={t(`landing.faq.items.${item}.question`)}
            >
              {t(`landing.faq.items.${item}.answer`)}
            </AccordionItem>
          ))}
        </div>
      </Container>
    </section>
  );
}
