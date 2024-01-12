document.addEventListener("DOMContentLoaded", function() {
    let totalSales = 0;
    const priceCells = document.querySelectorAll("#salesTable tbody td:nth-child(3)");

    priceCells.forEach(function(cell) {
      let priceText = cell.textContent.trim().replace("$", "");
      let price = parseFloat(priceText);
      if (!isNaN(price)) {
        totalSales += price;
      }
    });

    document.getElementById("totalSales").textContent = `$${totalSales.toFixed(2)}`;
});