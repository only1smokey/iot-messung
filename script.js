const refreshTime = 2000;
    let lastReading = "";

    function setRating(id, text, type) {
      const element = document.getElementById(id);
      element.textContent = text;
      element.dataset.type = type;
    }

    function rateTemperature(value) {
      if (value >= 20 && value <= 24) return ["Gut", "good"];
      if (value >= 18 && value <= 27) return ["In Ordnung", "warning"];
      return [value < 18 ? "Zu kalt" : "Zu warm", "bad"];
    }

    function rateHumidity(value) {
      if (value >= 40 && value <= 60) return ["Gut", "good"];
      if (value >= 30 && value <= 70) return ["In Ordnung", "warning"];
      return [value < 30 ? "Zu trocken" : "Zu feucht", "bad"];
    }

    function ratePressure(value) {
      if (value >= 980 && value <= 1040) return ["Normal", "good"];
      return ["Ungewöhnlich", "warning"];
    }

    function setConnection(connected) {
      document.getElementById("connectionStatus").textContent =
        connected ? "Datenbank verbunden" : "Keine Verbindung";

      document.getElementById("statusDot").dataset.connected =
        connected ? "true" : "false";
    }

    function setAverages(averages) {
      // put average on page
      if (!averages) {
        document.getElementById("avgTemperature").textContent = "--";
        document.getElementById("avgHumidity").textContent = "--";
        document.getElementById("avgPressure").textContent = "--";
        document.getElementById("avgCount").textContent = "Keine Daten";
        return;
      }

      document.getElementById("avgTemperature").textContent =
        Number(averages.temperature).toFixed(1);

      document.getElementById("avgHumidity").textContent =
        Number(averages.humidity).toFixed(1);

      document.getElementById("avgPressure").textContent =
        Number(averages.pressure).toFixed(1);

      document.getElementById("avgCount").textContent =
        `${averages.count} Messwerte`;
    }

    function clearPage() {
      lastReading = "";

      document.getElementById("temperature").textContent = "--";
      document.getElementById("humidity").textContent = "--";
      document.getElementById("pressure").textContent = "--";
      setAverages(null);

      setRating("temperatureRating", "Keine Daten", "muted");
      setRating("humidityRating", "Keine Daten", "muted");
      setRating("pressureRating", "Keine Daten", "muted");

      document.getElementById("lastUpdate").textContent =
        "Keine Messwerte vorhanden";

      document.getElementById("chart").innerHTML =
        '<span class="empty">Keine Messwerte vorhanden.</span>';
    }

    function buildPoints(values, width, height, padding, min, max) {
      const range = Math.max(0.001, max - min);

      return values.map((value, index) => {
        const x =
          padding.left +
          index / Math.max(1, values.length - 1) *
          (width - padding.left - padding.right);

        const y =
          padding.top +
          (max - value) / range *
          (height - padding.top - padding.bottom);

        return `${x.toFixed(1)},${y.toFixed(1)}`;
      }).join(" ");
    }

    function drawChart(readings) {
      const width = 1000;
      const height = 350;
      const padding = {left: 52, right: 55, top: 16, bottom: 35};

      const temperatures = readings.map(row => Number(row.temperature));
      const humidities = readings.map(row => Number(row.humidity));
      const pressures = readings.map(row => Number(row.pressure));

      const leftValues = temperatures.concat(humidities);
      const leftMin = Math.floor(Math.min(...leftValues) - 5);
      const leftMax = Math.ceil(Math.max(...leftValues) + 5);
      const pressureMin = Math.floor(Math.min(...pressures) - 2);
      const pressureMax = Math.ceil(Math.max(...pressures) + 2);

      const tempPoints = buildPoints(
        temperatures, width, height, padding, leftMin, leftMax
      );

      const humPoints = buildPoints(
        humidities, width, height, padding, leftMin, leftMax
      );

      const pressurePoints = buildPoints(
        pressures, width, height, padding, pressureMin, pressureMax
      );

      let grid = "";

      for (let i = 0; i <= 5; i++) {
        const y =
          padding.top +
          i * (height - padding.top - padding.bottom) / 5;

        const leftLabel =
          Math.round(leftMax - i * (leftMax - leftMin) / 5);

        const rightLabel =
          Math.round(pressureMax - i * (pressureMax - pressureMin) / 5);

        grid += `
          <line class="grid-line"
            x1="${padding.left}" y1="${y}"
            x2="${width - padding.right}" y2="${y}">
          </line>

          <text class="axis-text"
            x="${padding.left - 8}" y="${y + 4}"
            text-anchor="end">${leftLabel}</text>

          <text class="axis-text"
            x="${width - padding.right + 8}" y="${y + 4}"
            text-anchor="start">${rightLabel}</text>
        `;
      }

      const firstTime = new Date(readings[0].created_at)
        .toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});

      const middleTime = new Date(
        readings[Math.floor(readings.length / 2)].created_at
      ).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});

      const lastTime = new Date(readings[readings.length - 1].created_at)
        .toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});

      document.getElementById("chart").innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
          ${grid}
          <polyline class="temp-line" points="${tempPoints}"></polyline>
          <polyline class="hum-line" points="${humPoints}"></polyline>
          <polyline class="press-line" points="${pressurePoints}"></polyline>

          <text class="axis-text"
            x="${padding.left}" y="${height - 8}"
            text-anchor="start">${firstTime}</text>

          <text class="axis-text"
            x="${width / 2}" y="${height - 8}"
            text-anchor="middle">${middleTime}</text>

          <text class="axis-text"
            x="${width - padding.right}" y="${height - 8}"
            text-anchor="end">${lastTime}</text>
        </svg>
      `;
    }

    async function loadData() {
      // ask flask for data
      try {
        const response = await fetch("/api/readings", {cache: "no-store"});
        const data = await response.json();

        if (!response.ok || !data.ok) {
          throw new Error(data.error || "Unbekannter Fehler");
        }

        setConnection(true);
        document.getElementById("errorBox").style.display = "none";
        setAverages(data.averages);

        if (!data.latest) {
          clearPage();
          return;
        }

        const latest = data.latest;
        const temperature = Number(latest.temperature);
        const humidity = Number(latest.humidity);
        const pressure = Number(latest.pressure);

        document.getElementById("temperature").textContent =
          temperature.toFixed(1);

        document.getElementById("humidity").textContent =
          humidity.toFixed(1);

        document.getElementById("pressure").textContent =
          pressure.toFixed(1);

        setRating("temperatureRating", ...rateTemperature(temperature));
        setRating("humidityRating", ...rateHumidity(humidity));
        setRating("pressureRating", ...ratePressure(pressure));

        document.getElementById("lastUpdate").textContent =
          "Letzte Messung: " +
          new Date(latest.created_at).toLocaleString();

        if (latest.created_at !== lastReading) {
          lastReading = latest.created_at;
          drawChart(data.readings);
        }
      } catch (error) {
        setConnection(false);
        document.getElementById("errorText").textContent = error.message;
        document.getElementById("errorBox").style.display = "block";
      }
    }

    async function clearDatabase() {
      // user click clear db
      if (!confirm("Alle Messwerte aus der Datenbank löschen?")) {
        return;
      }

      const button = document.getElementById("clearButton");
      button.disabled = true;
      button.textContent = "Löschen...";

      try {
        const response = await fetch("/api/clear", {
          method: "POST",
          cache: "no-store"
        });

        const data = await response.json();

        if (!response.ok || !data.ok) {
          throw new Error(data.error || "Löschen fehlgeschlagen");
        }

        clearPage();
        setConnection(true);
        document.getElementById("errorBox").style.display = "none";
        button.textContent = `${data.deleted} gelöscht`;

        setTimeout(() => {
          button.textContent = "Clear DB";
        }, 1500);
      } catch (error) {
        document.getElementById("errorText").textContent = error.message;
        document.getElementById("errorBox").style.display = "block";
        button.textContent = "Clear DB";
      } finally {
        button.disabled = false;
      }
    }

    document
      .getElementById("clearButton")
      .addEventListener("click", clearDatabase);

    loadData();
    setInterval(loadData, refreshTime);
