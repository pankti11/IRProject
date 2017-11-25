import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

import org.jsoup.Jsoup;

public class DownloadDocs {
	public static void main(String[] args){

		File links = new File("links.txt");
		File wpFolder = new File("WebPages");
		ArrayList<String> pnames = new ArrayList<String>();
		int lineno= 0;
		
		try{
			wpFolder.mkdir();
			BufferedReader br = new BufferedReader(new FileReader(links));
			for(String line; (line = br.readLine()) != null; ) {
				String html = Jsoup.connect(line).get().html();
				
				PrintWriter out = new PrintWriter("WebPages"+File.separator+lineno+".html");
				out.print(html);
				//pnames.add(line.split("/wiki/")[1].replaceAll("[\\p{Punct}]", "")+"1.html");
				out.close();
				
				
				/*if(pnames.contains(line.split("/wiki/")[1].replaceAll("[\\p{Punct}]", "")+".html")){
					System.out.println(line.split("/wiki/")[1].replaceAll("[\\p{Punct}]", "")+".html");
					PrintWriter out = new PrintWriter("WebPages"+File.separator+line.split("/wiki/")[1].replaceAll("[\\p{Punct}]", "")+"1.html");
					out.print(html);
					pnames.add(line.split("/wiki/")[1].replaceAll("[\\p{Punct}]", "")+"1.html");
					out.close();
					
					}
				else{
					
					PrintWriter out = new PrintWriter("WebPages"+File.separator+line.split("/wiki/")[1].replaceAll("[\\p{Punct}]", "")+".html");
					out.print(html);
					pnames.add(line.split("/wiki/")[1].replaceAll("[\\p{Punct}]", "")+".html");
						out.close();
				}*/
				
				lineno++;
				System.out.println(lineno);
				
			
				
					
					
			}
			
			Set<String> set = new HashSet<String>(pnames);

			if(set.size() < pnames.size()){
			    /* There are duplicates */
				System.out.println("fdsgfdgdfsg");
			}
			// l		ine is not visible here.
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
