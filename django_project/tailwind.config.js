/** Tailwind CSS configuration for production CLI build.
 *  See README for the build command.
 */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./store/**/*.py",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        brand:  { DEFAULT: "#0c5faa", hover: "#094a85" },
        accent: { DEFAULT: "#4a9eff" },
        cta:    { DEFAULT: "#7ed321", hover: "#6bc218" },
      },
      fontFamily: {
        clash:  ["'Clash Display'", "sans-serif"],
        roboto: ["Roboto", "sans-serif"],
      },
      borderRadius: { brand: "0.625rem" },
    },
  },
  plugins: [],
};
