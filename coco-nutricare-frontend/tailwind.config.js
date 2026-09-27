/** Colours taken from the Coco NutriCare UI mockups. */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        coco: {
          bg: "#061a15",      // page background
          panel: "#0e2b24",   // cards
          line: "#1c463b",    // borders
          side: "#0a5446",    // sidebar
          green: "#0f7a5c",   // green buttons
          accent: "#22b889",  // green text / headings
          orange: "#f0932b",  // primary CTA
          mint: "#d9efe8",    // active nav item
          muted: "#8fb0a6",   // secondary text
        },
      },
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] },
    },
  },
  plugins: [],
};
