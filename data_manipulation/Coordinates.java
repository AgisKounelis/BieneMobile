import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;


public class Coordinates {
    private final static String KEY = "my_key";

    private final static String data[] = {

        "el Raval",
        "el Barri Gotic",
        "la Barceloneta",
        "Sant Pere, Santa Caterina i la Ribera",
        "el Fort Pienc",
        "la Sagrada Familia",
        "la Dreta de l Eixample",
        "l Antiga Esquerra de l Eixample",
        "la Nova Esquerra de l Eixample",
        "Sant Antoni",
        "el Poble Sec - AEI Parc Montjuic (1)",
        "la Marina del Prat Vermell - AEI Zona Franca (2)",
        "la Marina de Port",
        "la Font de la Guatlla",
        "Hostafrancs",
        "la Bordeta",
        "Sants - Badal",
        "Sants",
        "les Corts",
        "la Maternitat i Sant Ramon",
        "Pedralbes",
        "Vallvidrera, el Tibidabo i les Planes",
        "Sarrià",
        "les Tres Torres",
        "Sant Gervasi - la Bonanova",
        "Sant Gervasi - Galvany",
        "el Putxet i el Farro",
        "Vallcarca i els Penitents",
        "el Coll",
        "la Salut",
        "la Vila de Gràcia",
        "el Camp d en Grassot i Gràcia Nova",
        "el Baix Guinardo",
        "Can Baro",
        "el Guinardo",
        "la Font d en Fargues",
        "el Carmel",
        "la Teixonera",
        "Sant Genis dels Agudells",
        "Montbau",
        "la Vall d Hebron",
        "la Clota",
        "Horta",
        "Vilapicina i la Torre Llobeta",
        "Porta",
        "el Turo de la Peira",
        "Can Peguera",
        "la Guineueta",
        "Canyelles",
        "les Roquetes",
        "Verdun",
        "la Prosperitat",
        "la Trinitat Nova",
        "Torre Baro",
        "Ciutat Meridiana",
        "Vallbona",
        "la Trinitat Vella",
        "Baro de Viver",
        "el Bon Pastor",
        "Sant Andreu",
        "la Sagrera",
        "el Congrés i els Indians",
        "Navas",
        "el Camp de l Arpa del Clot",
        "el Clot",
        "el Parc i la Llacuna del Poblenou",
        "la Vila Olimpica del Poblenou",
        "el Poblenou",
        "Diagonal Mar i el Front Maritim del Poblenou",
        "el Besos i el Maresme",
        "Provençals del Poblenou",
        "Sant Marti de Provençals",
        "la Verneda i la Pau"

    };


    public static void main(String[] args) {
        try {
            File fout = new File("out.txt");
            FileOutputStream fos = new FileOutputStream(fout);

            BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(fos));

            String myURL = "http://www.mapquestapi.com/geocoding/v1/address";
            for (int i = 0; i < data.length; i++) {
                String myParams = "&key=" + KEY + "&location=" + data[counter] + ",Barcelona,Spain";
                String myResult = executePost(myURL, myParams);
                bw.write(myResult + " ");
            }

            bw.close();
        } catch (Exception e) {}
    }


    public static String executePost(String targetURL, String urlParameters) {
        HttpURLConnection connection = null;

        try {
            URL url = new URL(targetURL);
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setRequestProperty("Content-Type",
                "application/x-www-form-urlencoded");

            connection.setUseCaches(false);
            connection.setDoOutput(true);

            DataOutputStream wr = new DataOutputStream(
                connection.getOutputStream());
            wr.writeBytes(urlParameters);
            wr.close();

            InputStream is = connection.getInputStream();
            BufferedReader rd = new BufferedReader(new InputStreamReader(is));
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = rd.readLine()) != null) {
                response.append(line);
                response.append('\r');
            }
            rd.close();

            return response.toString();
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

}