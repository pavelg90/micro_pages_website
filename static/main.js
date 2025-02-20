// main.js

/********** Plan Selector Handling **********/
const planSelectForm = document.getElementById('plan-select-form');
const planTypeSelect = document.getElementById('plan_type');
const investmentSection = document.getElementById('investment-section');
const goalSection = document.getElementById('goal-section');

function updatePlanDisplay() {
  const selectedPlan = planTypeSelect.value;
  if (selectedPlan === 'investment') {
    investmentSection.style.display = 'block';
    goalSection.style.display = 'none';
  } else {
    investmentSection.style.display = 'none';
    goalSection.style.display = 'block';
  }
}

// Trigger display logic on load and whenever the user changes the dropdown
planTypeSelect.addEventListener('change', updatePlanDisplay);
updatePlanDisplay();

/********** Investment Calculator Section **********/
const investForm = document.getElementById('investment-form');
const initialAmountInput = document.getElementById('initial_amount');
const monthlyContributionInput = document.getElementById('monthly_contribution');
const annualInterestInput = document.getElementById('annual_interest');
const yearsInput = document.getElementById('years');
const finalAmountDisplay = document.getElementById('final_amount');
const chartContainer = document.getElementById('chartContainer');
const chartCanvas = document.getElementById('myChart');
let chart; // Chart.js instance

function debounce(func, delay) {
  let debounceTimer;
  return function(...args) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => func.apply(this, args), delay);
  };
}

function calculateFinalAmount(P, PMT, r, years) {
  const n = 12;
  if (r > 0) {
    return P * Math.pow(1 + r / n, n * years) + PMT * ((Math.pow(1 + r / n, n * years) - 1) / (r / n));
  } else {
    return P + PMT * n * years;
  }
}

function generateGraphDataMonthly(P, PMT, r, years) {
  const n = 12;
  const totalMonths = Math.round(years * 12);
  let labels = [];
  let principal = [];
  let interest = [];
  for (let i = 0; i <= totalMonths; i++) {
    let total;
    if (r > 0) {
      total = P * Math.pow(1 + r / n, i) + PMT * ((Math.pow(1 + r / n, i) - 1) / (r / n));
    } else {
      total = P + PMT * i;
    }
    let currPrincipal = P + PMT * i;
    let currInterest = total - currPrincipal;
    labels.push(i);
    principal.push(parseFloat(currPrincipal.toFixed(2)));
    interest.push(parseFloat(currInterest.toFixed(2)));
  }
  return { labels, principal, interest };
}

function generateGraphDataYearly(P, PMT, r, years) {
  const totalYears = Math.floor(years);
  let labels = [];
  let principal = [];
  let interest = [];
  for (let i = 0; i <= totalYears; i++) {
    const months = i * 12;
    let total;
    if (r > 0) {
      total = P * Math.pow(1 + r / 12, months) + PMT * ((Math.pow(1 + r / 12, months) - 1) / (r / 12));
    } else {
      total = P + PMT * months;
    }
    let currPrincipal = P + PMT * months;
    let currInterest = total - currPrincipal;
    labels.push(i);
    principal.push(parseFloat(currPrincipal.toFixed(2)));
    interest.push(parseFloat(currInterest.toFixed(2)));
  }
  return { labels, principal, interest };
}

function updateInvestmentCalculations() {
  const P = parseFloat(initialAmountInput.value);
  const PMT = parseFloat(monthlyContributionInput.value);
  const annualInterest = parseFloat(annualInterestInput.value);
  const years = parseFloat(yearsInput.value);

  if (isNaN(P) || isNaN(PMT) || isNaN(annualInterest) || isNaN(years) || years <= 0) {
    chartContainer.style.display = "none";
    finalAmountDisplay.textContent = "סכום סופי: 0 ₪";
    if (chart) {
      chart.destroy();
      chart = null;
    }
    return;
  }

  chartContainer.style.display = "block";
  const r = annualInterest / 100;
  const finalAmount = calculateFinalAmount(P, PMT, r, years);
  finalAmountDisplay.textContent = `סכום סופי: ${finalAmount.toFixed(2)} ₪`;

  let graphData;
  if (years < 2) {
    graphData = generateGraphDataMonthly(P, PMT, r, years);
  } else {
    graphData = generateGraphDataYearly(P, PMT, r, years);
  }

  if (chart) {
    chart.destroy();
  }
  const ctx = chartCanvas.getContext('2d');
  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: graphData.labels,
      datasets: [
        {
          label: 'הון מושקע',
          data: graphData.principal,
          backgroundColor: 'rgba(75, 192, 192, 0.5)',
          type: 'bar'
        },
        {
          label: 'ריבית דריבית',
          data: graphData.interest,
          borderColor: 'rgba(255, 99, 132, 1)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          type: 'line',
          fill: false,
          tension: 0.2
        }
      ]
    },
    options: {
      scales: {
        x: {
          title: {
            display: true,
            text: years < 2 ? 'חודשים' : 'שנים'
          }
        },
        y: {
          title: {
            display: true,
            text: 'סכום (₪)'
          }
        }
      },
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 0 }
    }
  });
}

const debouncedInvestmentUpdate = debounce(updateInvestmentCalculations, 300);
investForm.addEventListener('input', debouncedInvestmentUpdate);
investForm.addEventListener('submit', function(e) {
  e.preventDefault();
  debouncedInvestmentUpdate();
});

/********** Goal Planner Section **********/
const goalForm = document.getElementById('goal-form');

function updateGoalPlan() {
  const targetAmount = parseFloat(document.getElementById('target_amount').value);
  const targetYears = parseFloat(document.getElementById('target_years').value);
  const targetInterest = parseFloat(document.getElementById('target_interest').value);
  const recommendedInitial = document.getElementById('recommended_initial');
  const recommendedMonthly = document.getElementById('recommended_monthly');

  if (
    isNaN(targetAmount) ||
    isNaN(targetYears) ||
    targetYears <= 0 ||
    isNaN(targetInterest)
  ) {
    recommendedInitial.textContent = "הון התחלתי מומלץ: - ₪";
    recommendedMonthly.textContent = "הפקדה חודשית מומלצת: - ₪";
    return;
  }

  const n = 12;
  const r = targetInterest / 100;
  const totalMonths = targetYears * n;
  const compoundFactor = Math.pow(1 + r/n, totalMonths);
  const denominator = (totalMonths * compoundFactor) + ((compoundFactor - 1) / (r/n));

  const PMT = targetAmount / denominator;
  const initialDeposit = PMT * totalMonths;

  recommendedMonthly.textContent = `הפקדה חודשית מומלצת: ${PMT.toFixed(2)} ₪`;
  recommendedInitial.textContent = `הון התחלתי מומלץ: ${initialDeposit.toFixed(2)} ₪`;
}

const debouncedGoalUpdate = debounce(updateGoalPlan, 300);
goalForm.addEventListener('input', debouncedGoalUpdate);

/*
  No submission needed for goalForm since it's a live calculation.
  If you want to prevent default on submit, you could do so similarly:
  goalForm.addEventListener('submit', e => e.preventDefault());
*/

