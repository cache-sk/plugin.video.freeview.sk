<?
	require_once './Requests.php';
	Requests::register_autoloader();
	
	$options = array("verify" => false);
	$headers = array("Content-type"=>"application/x-www-form-urlencoded",
					"Accept-encoding"=>"gzip",
					"Connection"=>"Keep-Alive");
	$session = new Requests_Session(null, $headers, array(), $options);
	$session->useragent = "Dalvik/1.6.0 (Linux; U; Android 4.4.4; Nexus 7 Build/KTU84P)";
	$BASE = "https://www.ceskatelevize.cz";
	$TOKENURL = "/services/ivysilani/xml/token/";
	$PLAYLISTURL = "/services/ivysilani/xml/playlisturl/";

	if(!isset($_GET["sub"])){

		$data = array("user"=>"iDevicesMotion");
		$response = $session->post($BASE.$TOKENURL,array(), $data);
		
		$data = $response->body;
		$xml=simplexml_load_string($data);// or die("Error: Cannot create object from token");
		$token = (string)$xml;
		
		$data = array("token"=>$token,"quality"=>"web", "ID"=>"CT1", "playerType"=>"iPad");
		$response = $session->post($BASE.$PLAYLISTURL,array(), $data);
		$data = $response->body;
		$xml=simplexml_load_string($data);// or die("Error: Cannot create object from playlist url ".$xml);
		$playlist_url = (string)$xml;

		$response = $session->get($playlist_url);
		$data = $response->body;
		$xml=simplexml_load_string($data);// or die("Error: Cannot create object from playlist ".$xml);
		$res = $xml->xpath("/data/smilRoot/body/video/@src");
		$playlist_url2 = (string)$res[0][0];
		
		$response = $session->get($playlist_url2);
		$playlist_data = $response->body;
	
		$fp = fopen("php://memory", 'r+');
		fputs($fp, $playlist_data);
		rewind($fp);
		$playlist_data = "";
		$request_url = "http://$_SERVER[HTTP_HOST]$_SERVER[SCRIPT_NAME]?sub=";
		while($line = fgets($fp)){
			$line = trim($line);
  			if (substr($line, 0, 1) !== "#"){
  				$line = $request_url . urlencode ($line);
  			}
  			$playlist_data = $playlist_data . $line . "\n";
		}
		fclose($fp);
	
		echo $playlist_data;
	} else {
		$playlist = urldecode($_GET["sub"]);
		$playlist_prefix = substr($playlist, 0, strrpos( $playlist, '/'));

		$response = $session->get($playlist);
		$playlist_data = $response->body;

		$fp = fopen("php://memory", 'r+');
		fputs($fp, $playlist_data);
		rewind($fp);
		$playlist_data = "";

		while($line = fgets($fp)){
			$line = trim($line);
  			if (substr($line, 0, 1) !== "#"){
  				$line = $playlist_prefix . "/" . $line;
  			}
  			$playlist_data = $playlist_data . $line . "\n";
		}
		fclose($fp);
/*
		//header('Content-Type: text/plain');
		foreach($response->headers->getIterator() as $k => $v) {
			//echo $k . ":" . $v . "\n";
			if ($k !== "content-encoding"){
				header($k.":".$v);
			}
		}
		header('content-disposition: attachment; filename="playlist.m3u8"');
		
		*/
		echo $playlist_data;
		
	}
	
	
?>