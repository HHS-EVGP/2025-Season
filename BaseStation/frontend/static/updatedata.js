// Start initial chart instances
function startCharts() {
  fetch('/getdata')
    .then(response => response.json())
    .then(data => {

      //Destroy old charts if they exist
      if (window.throttleBrakeChart instanceof Chart) {
        window.throttleBrakeChart.destroy();
      }
      if (window.gpsChart instanceof Chart) {
        window.gpsChart.destroy();
      }

      const barCtx = document.getElementById('throttleBrakeChart');

      window.throttleBrakeChart = new Chart(barCtx, {
        type: 'bar',
        data: {
          labels: ['Throttle', 'Brake Pedal'],
          datasets: [{
            data: [data.throttle ?? 0, data.brake_pedal ?? 0],
            backgroundColor: ['rgba(75, 192, 192, 0.2)', 'rgba(255, 99, 132, 0.2)'],
            borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)'],
            borderWidth: 1
          }]
        },
        options: {
          animation: false,
          indexAxis: 'y',
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            x: {
              beginAtZero: true
            },
            y: {
              ticks: {
                font: {
                  size: 16 // Adjust the font size for the labels
                }
              }
            }
          }
        }
      });

      const ctx = document.getElementById('gpsplot');

      window.gpsChart = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [{
            data: [{
              x: data.GPS_x,
              y: data.GPS_y
            }],
            backgroundColor: 'rgb(255, 99, 132)'
          }]
        },
        options: {
          plugins: {
            legend: {
              display: false,
            }
          },
          animation: false,
        }
      });
    });
}

// Update a variable on the server
function updateServerVariable(updatecode) {
  fetch('/usrupdate', {
    method: 'POST',
    body: updatecode,
  })
}


// Update data
function updateData() {
  fetch('/getdata')
    .then(response => response.json())
    .then(data => {

      // Statuses
      document.getElementById('systime').textContent = data.systime ?? 'XXX';
      document.getElementById('timestamp').textContent = data.timestamp ?? 'XXX';

      // Update the throttle and brake chart
      window.throttleBrakeChart.data.datasets[0].data = [data.throttle ?? 0, data.brake_pedal ?? 0];
      window.throttleBrakeChart.update();

      // Temperatures
      document.getElementById('motor_temp').textContent = data.motor_temp ?? 'XXX';
      document.getElementById('batt_1').textContent = data.batt_1 ?? 'XXX';
      document.getElementById('batt_2').textContent = data.batt_2 ?? 'XXX';
      document.getElementById('batt_3').textContent = data.batt_3 ?? 'XXX';
      document.getElementById('batt_4').textContent = data.batt_4 ?? 'XXX';

      // General
      document.getElementById('amp_hours').textContent = data.amp_hours ?? 'XXX.XXX';
      document.getElementById('voltage').textContent = data.voltage ?? 'XXX';
      document.getElementById('current').textContent = data.current ?? 'XXX';
      document.getElementById('speed').textContent = data.speed ?? 'XXX';
      document.getElementById('miles').textContent = data.miles ?? 'XXX.XXX';

      // Laps and pace
      document.getElementById('laps').textContent = data.laps ?? 'XX';
      document.getElementById('laptime').textContent = data.laptime ?? 'XXX';
      document.getElementById('targetlaptime').textContent = data.targetlaptime ?? 'XXX';

      //Amp hours remaining
      document.getElementById('capBudget').textContent = data.capBudget ?? 'XXX.XXX';

      // Start/stop race button
      let racing = data.racing ?? false;
      if (racing == true) {
        document.getElementById('racing').textContent = "Stop Race";
      }
      if (racing == false) {
        document.getElementById('racing').textContent = "Start Race"
      }

      // GPS
      document.getElementById('GPS_x').textContent = data.GPS_x ?? 'XXX';
      document.getElementById('GPS_y').textContent = data.GPS_y ?? 'XXX';

      // Update scatter plot with new gps data
      window.gpsChart.data.datasets[0].data.push({
        x: data.GPS_x,
        y: data.GPS_y
      });

      // Limit the number of points in the scatter plot
      if (window.gpsChart.data.datasets[0].data.length > data.maxgpspoints ?? 100) {
        window.gpsChart.data.datasets[0].data.shift();
      }

      window.gpsChart.update();

    });
}
setInterval(updateData, 250); // Update every 250ms

// Call startCharts on window load and resize
window.addEventListener('load', startCharts);
window.addEventListener('resize', startCharts);