/* main.js – NBA Playoffs Dashboard */

document.addEventListener('DOMContentLoaded', () => {

  // ── Chart defaults ──
  Chart.defaults.color = '#8888aa';
  Chart.defaults.borderColor = '#2a2a40';
  Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";

  const homeColor = GAME.homeColor;
  const awayColor = GAME.awayColor;

  // ── 1. Cumulative scoring line chart (Overview) ──
  const cumCtx = document.getElementById('cumulativeChart');
  if (cumCtx) {
    new Chart(cumCtx, {
      type: 'line',
      data: {
        labels: GAME.cumulative.labels,
        datasets: [
          {
            label: GAME.awayAbbr,
            data: GAME.cumulative.away,
            borderColor: awayColor,
            backgroundColor: awayColor + '33',
            fill: true,
            tension: 0.35,
            pointRadius: 5,
            pointHoverRadius: 7,
            borderWidth: 2.5,
          },
          {
            label: GAME.homeAbbr,
            data: GAME.cumulative.home,
            borderColor: homeColor,
            backgroundColor: homeColor + '33',
            fill: true,
            tension: 0.35,
            pointRadius: 5,
            pointHoverRadius: 7,
            borderWidth: 2.5,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 12, padding: 16 } },
          tooltip: { mode: 'index', intersect: false },
        },
        scales: {
          y: { beginAtZero: true, grid: { color: '#2a2a4088' } },
          x: { grid: { color: '#2a2a4044' } },
        },
      },
    });
  }

  // ── 2. Quarter-by-quarter grouped bar charts ──
  const QUARTERS = ['1st', '2nd', '3rd', '4th'];
  QUARTERS.forEach((q, idx) => {
    const ctx = document.getElementById(`quarterChart${q}`);

    if (!ctx) return;

    // Highlight this quarter's bars
    const homeData = GAME.quarterBars.home.map((v, i) =>
      i === idx ? homeColor : homeColor + '55'
    );
    const awayData = GAME.quarterBars.away.map((v, i) =>
      i === idx ? awayColor : awayColor + '55'
    );

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: GAME.quarterBars.labels,
        datasets: [
          {
            label: GAME.awayAbbr,
            data: GAME.quarterBars.away,
            backgroundColor: awayData,
            borderRadius: 6,
            borderSkipped: false,
          },
          {
            label: GAME.homeAbbr,
            data: GAME.quarterBars.home,
            backgroundColor: homeData,
            borderRadius: 6,
            borderSkipped: false,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 10, padding: 12 } },
          tooltip: { mode: 'index', intersect: false },
        },
        scales: {
          y: { beginAtZero: true, grid: { color: '#2a2a4088' } },
          x: { grid: { display: false } },
        },
      },
    });
  });


  // ── 3. Side-nav dot highlighting on scroll ──
  const container = document.getElementById('scrollContainer');
  const sections  = document.querySelectorAll('.scroll-section');
  const navDots   = document.querySelectorAll('.nav-dot');

  if (container && sections.length && navDots.length) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.id;
            navDots.forEach((dot) => {
              dot.classList.toggle('active', dot.getAttribute('href') === `#${id}`);
            });
          }
        });
      },
      {
        root: container,
        threshold: 0.5,
      }
    );

    sections.forEach((s) => observer.observe(s));
  }
});
