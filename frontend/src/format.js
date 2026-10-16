// Small helpers for showing numbers and dates nicely.

// 1200000 -> "₹12,00,000" (Indian digit grouping)
export function formatMoney(amount) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);
}

// 1200000 -> "₹12L" (L = lakh = 1,00,000), for short labels such as chart axes
export function formatLakhs(amount) {
  return `₹${Number((amount / 100000).toFixed(1))}L`;
}

// "2019-03-11" -> "Mar 11, 2019"
export function formatDate(isoDate) {
  const [year, month, day] = isoDate.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}
