/* pdg.sc

   This script returns a complete PDG for functions matching a regex, or the whole CPG if no regex is specified. The PDG
   is represented as two lists, one for the edges and another for the vertices.

   The first list contains all of the edges in the PDG. The first entry in each tuple contains the ID of the incoming
   vertex. The second entry in the tuple contains the ID of the outgoing vertex.

   The second list contains all the vertices in the PDG. The first entry in each tuple contains the ID of the vertex
   and the second entry contains the code stored in the vertex.
*/

import gremlin.scala.{Edge, GremlinScala}

import io.shiftleft.codepropertygraph.generated.EdgeTypes

import scala.collection.mutable

import java.io.PrintWriter  
import java.io.File  
import scala.reflect.io.Directory 
import scala.collection.mutable.Set 
import java.util.Date

type EdgeEntry = (AnyRef, AnyRef)
type VertexEntry = (AnyRef, String)
type Pdg = (Option[String], List[EdgeEntry], List[VertexEntry])


private def pdgFromEdges(edges: GremlinScala[Edge], filename: String, outFilePath: String): List[EdgeEntry] = {
  val filteredEdges = edges.filter(edge => edge.hasLabel(EdgeTypes.REACHING_DEF, EdgeTypes.CDG)).dedup.l
  //val filteredEdges = edges.dedup.l

  val edgeResult =
    filteredEdges.foldLeft(mutable.Set.empty[EdgeEntry]) {
      case (edgeList, edge) =>
        val edgeEntry = (edge.outVertex().property("LINE_NUMBER").orElse(""), edge.inVertex().property("LINE_NUMBER").orElse(""))
		//val edgeEntry = (edge.inVertex().id, edge.outVertex().id)
        //val inVertexEntry = (edge.inVertex().id, edge.inVertex().property("LINE_NUMBER").orElse(""))
		//val inVertexEntry = (edge.inVertex().id, edge.inVertex().property("CODE").orElse(""))
        //val outVertexEntry = (edge.outVertex().id, edge.outVertex().property("LINE_NUMBER").orElse(""))
		//val outVertexEntry = (edge.outVertex().id, edge.outVertex().property("CODE").orElse(""))

        edgeList += edgeEntry
    }
  edgeResult.toList |> outFilePath+"\\"+filename
  
  return edgeResult.toList
}

def subdirs2(dir: File): Array[File] = {
		//val d = dir.listFiles.filter(_.isDirectory)
		val f = dir.listFiles.filter(_.isFile)//.toIterator
		//f ++ d.toIterator.flatMap(subdirs2 _)
		
		return f
	}

// inFile: The path to the extracted functions, eg: F:/data/self_vul_repo/functions/Bad
// outFile: The path to restore the result, eg: F:/data/self_vul_repo/functions/Bad/BadFunc_lines
//flag = "src" or "vul"
@main def main(cpgFile: String, inFile: String, outFile: String, flag: String): Unit = {
	//val it = subdirs2(new File("F:\\data\\self_vul_repo\\functions\\Bad"))
	loadCpg(cpgFile)
	val it = subdirs2(new File(inFile))
	var start_time =new Date().getTime
	for(d <- it){
		val fileName = d.getName()
		var methodName = ""
		if(flag == "vul")
		{
			methodName = d.getName().split("\\$",0)(2).dropRight(2)
		}
		else if(flag == "src")
		{
			methodName = d.getName.split("\\$",0)(1)
		}
		else
		{
			println("[-]wrong flag value.")
			sys.exit()
		}
		println(methodName)
		try{
		  cpg.method(methodName).l.map{method =>
          val edgeEntries = pdgFromEdges(method.asScala.out().flatMap(_.asScala.outE()), fileName, outFile)
		  }
		}catch {
        case ex: Exception => println("error message:" + ex.getMessage)
      }
	}
	var end_time =new Date().getTime
	var runTime = (end_time - start_time)/1000.0
	println("runTime: " + runTime + " s")
}
