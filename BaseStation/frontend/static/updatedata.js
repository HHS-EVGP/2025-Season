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
            backgroundColor: ['rgba(68, 192, 95, 0.75)', 'rgba(245, 90, 90, 0.75)'],
            borderColor: ['rgb(68, 192, 95)', 'rgb(245, 90, 90)'],
            borderWidth: 1
          }]
        },
        options: {
          maintainAspectRatio: false,
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
            backgroundColor: 'rgb(54, 67, 126)'
          }]
        },
        options: {
          maintainAspectRatio: false,
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


// Authenticate lap controls
function authenticateLapControls(code) {
  fetch('/usrauth', {
    method: 'POST',
    body: code,
  })

  .then(response => {
    if (response.status == 200) {
      document.getElementById('lapcontrols').style.display = 'block';
      document.getElementById('authlapcontrols').style.display = 'none';
    }
    else if (response.status == 401) {
      new bootstrap.Modal(document.getElementById('lapauthmodal')).show();
      document.getElementById('autherror').style.display = 'block';
    }
    else {
      console.error('Unknown Auth Error:', response);
    }
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
      document.getElementById('systime').textContent = data.systime ?? 'NNN';
      document.getElementById('timestamp').textContent = data.timestamp ?? 'NNN';

      // Update the throttle and brake chart
      window.throttleBrakeChart.data.datasets[0].data = [data.throttle ?? 0, data.brake_pedal ?? 0];
      window.throttleBrakeChart.update();

      // Temperatures
      document.getElementById('motor_temp').textContent = data.motor_temp ?? 'NNN';
      document.getElementById('batt_1').textContent = data.batt_1 ?? 'NNN';
      document.getElementById('batt_2').textContent = data.batt_2 ?? 'NNN';
      document.getElementById('batt_3').textContent = data.batt_3 ?? 'NNN';
      document.getElementById('batt_4').textContent = data.batt_4 ?? 'NNN';

      // Check if any temperature is above 50 degrees and turn them red
      ['motor_temp', 'batt_1', 'batt_2', 'batt_3', 'batt_4'].forEach(id => {
        const element = document.getElementById(id);
        const value = parseFloat(data[id]) ?? 0;
        if (value > 50) {
          element.style.color = 'red';
        } else {
          element.style.color = ''; // Reset to default
        }
      });

      // General
      document.getElementById('amp_hours').textContent = data.amp_hours ?? 'NNN.NNN';
      document.getElementById('voltage').textContent = data.voltage ?? 'NNN';
      document.getElementById('current').textContent = data.current ?? 'NNN';
      document.getElementById('speed').textContent = data.speed ?? 'NNN';
      document.getElementById('miles').textContent = data.miles ?? 'NNN.NNN';

      // Laps and pace
      document.getElementById('laps').textContent = data.laps ?? 'XX';
      document.getElementById('laptime').textContent = data.laptime ?? 'NNN';
      document.getElementById('targetlaptime').textContent = data.targetlaptime ?? 'NNN';

      //Amp hours remaining in lap
      document.getElementById('capbudget').textContent = data.capbudget ?? 'NNN.NNN';

      // Start/stop race button
      const racing = data.racing ?? false;
      if (racing == true) {
        document.getElementById('racing').textContent = "Stop Race";
      }
      if (racing == false) {
        document.getElementById('racing').textContent = "Start Race"
      }

      // GPS
      document.getElementById('GPS_x').textContent = data.GPS_x ?? 'NNN';
      document.getElementById('GPS_y').textContent = data.GPS_y ?? 'NNN';

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


// Hide lap controls by default
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('lapcontrols').style.display = 'none';
  document.getElementById('autherror').style.display = 'none';
});
