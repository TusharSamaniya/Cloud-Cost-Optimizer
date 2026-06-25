/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class', // Step 8
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}", // Step 5
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}