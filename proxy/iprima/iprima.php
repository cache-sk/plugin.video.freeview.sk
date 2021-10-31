<?
	//dependency - Requests for php
	//https://requests.ryanmccue.info/
	//https://github.com/rmccue/Requests
	
	require_once("iconfig.php");
	
	$isTest = isset($_GET["test"]);
	
	if (!$isTest && $USERNAME !== "" && $PASSWORD !== ""){
		if (!isset($_SERVER['PHP_AUTH_USER']) ||
			($_SERVER['PHP_AUTH_USER'] !== $USERNAME && $_SERVER['PHP_AUTH_PW'] !== $PASSWORD)) {
			header('WWW-Authenticate: Basic realm="kodi tools"');
			header('HTTP/1.0 401 Unauthorized');
			echo 'CHSKYM?';
			exit;
		}
	}
	
	if ((isset($_GET["ch"]) && isset($CHANNELS[$_GET["ch"]])) || ($isTest && isset($_GET["ch"]))){
		
		try { //info log
			$requests = file_get_contents("rcount");
			$requests++;
			file_put_contents("rcount",$requests);
		} catch (Exception $e) {
			//ignore
		}
		
		
		require_once './Requests.php';
		Requests::register_autoloader();
		
		$channel = $isTest ? $CHANNELS["prima"] : $CHANNELS[$_GET["ch"]];
		$name = $isTest ? "test" : $_GET["ch"];

		$options = array("verify" => false);
		$headers = array();
		$session = new Requests_Session(null, $headers, array(), $options);
		$session->useragent = $UA;
		$response = $session->get($channel[0]);
		$session->headers['Referer'] = $channel[0];
		$response = $session->get($channel[1]);
		$data = $response->body;
		preg_match_all('/"url" : "http(.*).m3u8",/', $data, $match);
		$playlist = "http" . $match[1][0] . ".m3u8";
		
		$options = array("verify" => false);
		$headers = array();
		$session = new Requests_Session(null, $headers, array(), $options);
		$session->useragent = $UA;
		$response = $session->get($playlist);
		$playlist_data = $response->body;
		
		$fp = fopen("php://memory", 'r+');
		fputs($fp, $playlist_data);
		rewind($fp);
		$playlist_data = "";
		$playlist_prefix = substr($playlist, 0, strrpos( $playlist, '/'));
		$request_url = "http://$_SERVER[HTTP_HOST]$_SERVER[SCRIPT_NAME]?sub=";
		while($line = fgets($fp)){
			$line = trim($line);
  			if (substr($line, 0, 1) !== "#"){
  				$line = $request_url . urlencode ($playlist_prefix . "/" . $line);
  				if ($isTest) {
  					$playlist_data = $line . "&test=1\n";
  					break;
  				}
  			}
  			if (!$isTest) $playlist_data = $playlist_data . $line . "\n";
  			
		}
		fclose($fp);
		
		//header('Content-Type: text/plain');
		foreach($response->headers->getIterator() as $k => $v) {
			//echo $k . ":" . $v . "\n";
			if ($k !== "content-encoding"){
				header($k.":".$v);
			}
		}
		header('content-disposition: attachment; filename="'.$name.'.m3u8"');
		
		echo $playlist_data;
	} elseif (isset($_GET["sub"])){
		$crypto = "#EXT-X-KEY";
		$playlist = urldecode($_GET["sub"]);
		$playlist_prefix = substr($playlist, 0, strrpos( $playlist, '/'));
		require_once './Requests.php';
		Requests::register_autoloader();
		$options = array("verify" => false);
		$headers = array();
		$session = new Requests_Session(null, $headers, array(), $options);
		$session->useragent = $UA;
		$response = $session->get($playlist);
		$playlist_data = $response->body;

		$fp = fopen("php://memory", 'r+');
		fputs($fp, $playlist_data);
		rewind($fp);
		$playlist_data = "";
		$playlist_prefix = substr($playlist, 0, strrpos( $playlist, '/'));
		$request_url = "http://$_SERVER[HTTP_HOST]$_SERVER[SCRIPT_NAME]?crypto=";
		while($line = fgets($fp)){
			$line = trim($line);
  			if (substr($line, 0, 1) !== "#"){
  				$line = $playlist_prefix . "/" . $line;
  			} elseif (strlen($line) > strlen($crypto) && substr($line, 0, strlen($crypto)) === $crypto) {
  				preg_match('/(.*URI=")(.*)(".*)/', $line, $matches);
  				if ($isTest){
  					$playlist_data = $request_url . urlencode($matches[2]) . "\n";
  					break;
  				} else {
	  				$line = $matches[1]. $request_url . urlencode($matches[2]) . $matches[3];
  				}
  			}
  			if (!$isTest) $playlist_data = $playlist_data . $line . "\n";
		}
		fclose($fp);

		//header('Content-Type: text/plain');
		foreach($response->headers->getIterator() as $k => $v) {
			//echo $k . ":" . $v . "\n";
			if ($k !== "content-encoding"){
				header($k.":".$v);
			}
		}
		header('content-disposition: attachment; filename="playlist.m3u8"');
		echo $playlist_data;
	} elseif (isset($_GET["crypto"])){
		$crypto = urldecode($_GET["crypto"]);
		require_once './Requests.php';
		Requests::register_autoloader();
		$options = array("verify" => false);
		$headers = array();
		$session = new Requests_Session(null, $headers, array(), $options);
		$session->useragent = $UA;
		$response = $session->get($crypto);
		$crypto_data = $isTest ? "OK" : $response->body;
		foreach($response->headers->getIterator() as $k => $v) {
			//echo $k . ":" . $v . "\n";
			if ($k !== "content-encoding"){
				header($k.":".$v);
			}
		}
		//header('content-disposition: attachment; filename="playlist.m3u8"');
		echo $crypto_data;
	}
?>