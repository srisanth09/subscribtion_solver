/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        veri: {
          bg: '#f4f1ff',
          primary: '#6f55ef',
          dark: '#5136db',
          text: '#17132d',
          pink: '#ff3c6e',
          cyan: '#68c7ff',
          subtle: '#ede8ff',
        },
        guardian: {
          50: '#f8f6ff',
          100: '#ede8ff',
          200: '#dcd3fd',
          300: '#b8a6fa',
          400: '#8e75f5',
          500: '#6f55ef',
          600: '#5c3ee6',
          700: '#5136db',
          800: '#3d25b5',
          900: '#17132d',
        }
      }
    },
  },
  plugins: [],
}
