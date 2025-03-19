

    // <!-- Script for Feych stoch dat -->

    async function fetchStockData() {
        try {
            let response = await fetch("/api/stocks", { headers: { "X-Requested-With": "XMLHttpRequest" } });
            let data = await response.json();

            let stocks = data.map(stock => `${stock.name}: ₹${stock.price} (${stock.percent_change}%)`);
            document.getElementById("stock-marquee").innerText = stocks.join(" | ");
        } catch (error) {
            console.error("Error fetching stock data", error);
        }
    }

    setInterval(fetchStockData, 5000); // Refresh every 5 seconds
    fetchStockData();


    // <!-- Script for  Investment Goal Calculator -->
    function calculateInvestment() {
        let goalAmount = document.getElementById("goal-amount").value;
        let years = document.getElementById("years").value;
        let returnRate = document.getElementById("return-rate").value / 100;

        if (!goalAmount || !years || !returnRate) {
            alert("Please fill in all fields");
            return;
        }

        let monthlyInvestment = (goalAmount / ((Math.pow(1 + returnRate, years) - 1) / returnRate)) / 12;
        document.getElementById("investment-result").innerText = `You need to invest ₹${monthlyInvestment.toFixed(2)} per month.`;
    }


    // <!-- Script for storing local storage of investment -->

    document.addEventListener("DOMContentLoaded", function () {
        let investmentData = JSON.parse(localStorage.getItem("investmentData")) || {
            'Mutual Funds': 40,
            'Stocks': 30,
            'SIPs': 20,
            'Other Investments': 10
        };

        function updateChart() {
            chart.data.datasets[0].data = Object.values(investmentData);
            chart.update();
        }

        const ctx = document.getElementById('investmentPieChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(investmentData),
                datasets: [{
                    data: Object.values(investmentData),
                    backgroundColor: ['rgba(75, 192, 192, 0.7)', 'rgba(255, 99, 132, 0.7)',
                        'rgba(255, 205, 86, 0.7)', 'rgba(153, 102, 255, 0.7)'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' },
                    title: { display: true, text: 'Your Investment Distribution' }
                }
            }
        });


        // <!-- Script for generating finance facts -->

        document.getElementById("investment-form").addEventListener("submit", function (event) {
            event.preventDefault();
            const type = document.getElementById("investment-type").value;
            const amount = parseInt(document.getElementById("investment-amount").value);

            investmentData[type] += amount;
            localStorage.setItem("investmentData", JSON.stringify(investmentData));
            updateChart();
        });
    });


    document.addEventListener("DOMContentLoaded", function () {
        fetch("/get_finance_fact")
            .then(response => response.json())
            .then(data => {
                document.getElementById("finance-fact").innerHTML = "Did you know? " + data.fact;  // Use innerHTML to support bold text
            })
            .catch(error => {
                console.error("Error fetching finance fact:", error);
                document.getElementById("finance-fact").innerText = "Finance is fascinating!";
            });
    });