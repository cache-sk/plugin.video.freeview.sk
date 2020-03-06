<html>
	<head>
		<title>kodi tools</title>
	</head>
	<body>
		Stranka sluzi na ziskanie streamov free vysielania.<br/>
		Neprenasa ziadne velke binarne data.<br/>
		<button id="test">Spustit test funkcnosti</button><br/>
		<pre id="result"></pre>
	</body>
	<script>
		document.getElementById("test").onclick = function(event){
			var button = document.getElementById("test");
			var div = document.getElementById("result");
			var log = function(text){ div.innerHTML = div.innerHTML + "\n[" + (new Date()).toLocaleTimeString() + "]: " + text;};
			button.disabled = true;
			log("Start testu.");
			log("Prvy krok...");
			var xhr = new XMLHttpRequest();
			xhr.ontimeout = function () {
        		log("Chyba: cas vyprsal.");
        		button.disabled = false;
    		};
			xhr.open('GET', 'iprima.php?ch=test&test=1');
			xhr.send();
			xhr.onload = function() {
				if (xhr.readyState === 4 && xhr.status === 200 && 
					(xhr.getResponseHeader("content-type").includes("application/vnd.apple.mpegurl") || xhr.getResponseHeader("content-type").includes("application/octet-stream"))){
					log("OK");
					if (xhr.getResponseHeader("content-type").includes("application/vnd.apple.mpegurl")){
						log("Dalsi krok... ");
						var next = location.protocol === 'https:' ? xhr.responseText.replace("http:","https:") : xhr.responseText;
						xhr.open('GET', next);
						xhr.send();
					} else {
						log("Test skoncil.\n");
						button.disabled = false;
					}
	    		} else {
	    			log("Chyba!");
	    			button.disabled = false;
	    		}
	    	}
		};
	</script>
</html>