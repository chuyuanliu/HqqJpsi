#include <iostream>
#include <iomanip>
#include <cstdio>
#include <TROOT.h>
#include <boost/bind.hpp>
#include <signal.h>

#include "HqqJpsi/nTupleAnalysis/interface/analysis.h"
#include "nTupleAnalysis/baseClasses/interface/helpers.h"

using std::cout;  using std::endl;

using namespace HqqJpsi;

analysis::analysis(TChain* _events, TChain* _runs, TChain* _lumiBlocks, fwlite::TFileService& fs, bool _isMC, bool _blind, std::string _year, std::string histDetailLevel, 
		   bool _debug, bool _fastSkim, 
		   std::string bjetSF, std::string btagVariations,
		   std::string JECSyst, std::string friendFile){
  if(_debug) std::cout<<"In analysis constructor"<<std::endl;
  debug      = _debug;
  isMC       = _isMC;
  blind      = _blind;
  year       = _year;
  events     = _events;

  events->SetBranchStatus("*", 0);

  //keep branches needed for JEC Uncertainties
  if(isMC){
    events->SetBranchStatus("nGenJet"  , 1);
    events->SetBranchStatus( "GenJet_*", 1);
    //events->SetBranchStatus("Jet_genJetIdxG", 1);
  }
  events->SetBranchStatus(   "MET*", 1);
  events->SetBranchStatus("RawMET*", 1);
  events->SetBranchStatus("fixedGridRhoFastjetAll", 1);
  events->SetBranchStatus("Jet_rawFactor", 1);
  events->SetBranchStatus("Jet_area", 1);
  events->SetBranchStatus("Jet_neEmEF", 1);
  events->SetBranchStatus("Jet_chEmEF", 1);

  if(JECSyst!=""){
    std::cout << "events->AddFriend(\"Friends\", "<<friendFile<<")" << " for JEC Systematic " << JECSyst << std::endl;
    events->AddFriend("Friends", friendFile.c_str());
  }

  runs       = _runs;
  fastSkim = _fastSkim;
  

  //Calculate MC weight denominator
  if(isMC){
    if(debug) runs->Print();
    runs->SetBranchStatus("*", 0);
    Long64_t loadStatus = runs->LoadTree(0);
    if(loadStatus < 0){
      std::cout << "ERROR in loading tree for entry index: " << 0 << "; load status = " << loadStatus << std::endl;
      std::exit(EXIT_FAILURE);
    }
    if(runs->FindBranch("genEventCount")){
      std::cout << "Runs has genEventCount" << std::endl;
      inputBranch(runs, "genEventCount", genEventCount);
      inputBranch(runs, "genEventSumw",  genEventSumw);
      inputBranch(runs, "genEventSumw2", genEventSumw2);
    }else{//for some presumably idiotic reason, NANOAODv6 added an underscore to these branch names...
      std::cout << "Runs has genEventCount_" << std::endl;
      inputBranch(runs, "genEventCount_", genEventCount);
      inputBranch(runs, "genEventSumw_",  genEventSumw);
      inputBranch(runs, "genEventSumw2_", genEventSumw2);      
    }
    for(int r = 0; r < runs->GetEntries(); r++){
      runs->GetEntry(r);
      mcEventCount += genEventCount;
      mcEventSumw  += genEventSumw;
      mcEventSumw2 += genEventSumw2;
    }
    cout << "mcEventCount " << mcEventCount << " | mcEventSumw " << mcEventSumw << endl;
  }

  lumiBlocks = _lumiBlocks;
  event      = new eventData(events, isMC, year, debug, fastSkim, bjetSF, btagVariations, JECSyst);   
  treeEvents = events->GetEntries();
//  cutflow    = new tagCutflowHists("cutflow", fs, isMC, debug);
//  if(isDataMCMix){
//    cutflow->AddCut("mixedEventIsData_3plus4Tag");
//    cutflow->AddCut("mixedEventIsMC_3plus4Tag");
//    cutflow->AddCut("mixedEventIsData");
//    cutflow->AddCut("mixedEventIsMC");
//  }
//  cutflow->AddCut("lumiMask");
//  cutflow->AddCut("HLT");
//  cutflow->AddCut("jetMultiplicity");
//  cutflow->AddCut("bTags");
//  cutflow->AddCut("DijetMass");
//  // cutflow->AddCut("MDRs");
//  if(nTupleAnalysis::findSubStr(histDetailLevel,"passMjjOth"))      cutflow->AddCut("MjjOth");

//  lumiCounts    = new lumiHists("lumiHists", fs, year, false, debug);

  if(nTupleAnalysis::findSubStr(histDetailLevel,"allEvents"))     allEvents      = new eventHists("allEvents",     fs, isMC, blind, histDetailLevel, debug);
  if(nTupleAnalysis::findSubStr(histDetailLevel,"HLTStudy"))      Dimuon0_Jpsi   = new eventHists("Dimuon0_Jpsi",   fs, isMC, blind, histDetailLevel, debug);
  if(nTupleAnalysis::findSubStr(histDetailLevel,"HLTStudy"))      Dimuon25_Jpsi  = new eventHists("Dimuon25_Jpsi",   fs, isMC, blind, histDetailLevel, debug);
  if(nTupleAnalysis::findSubStr(histDetailLevel,"preSel"))        preSel         = new eventHists("preSel",     fs, isMC, blind, histDetailLevel, debug);
  if(nTupleAnalysis::findSubStr(histDetailLevel,"bTags"))         bTags          = new eventHists("bTags",     fs, isMC, blind, histDetailLevel, debug);

//  if(nTupleAnalysis::findSubStr(histDetailLevel,"passPreSel"))    passPreSel    = new   tagHists("passPreSel",    fs, true,  isMC, blind, histDetailLevel, debug);
//  if(nTupleAnalysis::findSubStr(histDetailLevel,"pass4Jets"))     pass4Jets     = new   tagHists("pass4Jets",     fs, true,  isMC, blind, histDetailLevel, debug);
//  if(nTupleAnalysis::findSubStr(histDetailLevel,"pass4AllJets"))  pass4AllJets  = new   tagHists("pass4AllJets",  fs, true,  isMC, blind, histDetailLevel, debug);
//  //if(nTupleAnalysis::findSubStr(histDetailLevel,"passDijetMass")) passDijetMass = new   tagHists("passDijetMass", fs, true,  isMC, blind, histDetailLevel, debug);
//  // if(nTupleAnalysis::findSubStr(histDetailLevel,"passMDRs"))      passMDRs      = new   tagHists("passMDRs",      fs, true,  isMC, blind, histDetailLevel, debug);
//  if(nTupleAnalysis::findSubStr(histDetailLevel,"passSvB"))       passSvB       = new   tagHists("passSvB",       fs, true,  isMC, blind, histDetailLevel, debug);
//  if(nTupleAnalysis::findSubStr(histDetailLevel,"passMjjOth"))    passMjjOth    = new   tagHists("passMjjOth",    fs, true,  isMC, blind, histDetailLevel, debug);
//  if(nTupleAnalysis::findSubStr(histDetailLevel,"failrWbW2"))     failrWbW2     = new   tagHists("failrWbW2",     fs, true,  isMC, blind, histDetailLevel, debug);
//  if(nTupleAnalysis::findSubStr(histDetailLevel,"passMuon"))      passMuon      = new   tagHists("passMuon",      fs, true,  isMC, blind, histDetailLevel, debug);
//  if(nTupleAnalysis::findSubStr(histDetailLevel,"passDvT05"))     passDvT05     = new   tagHists("passDvT05",     fs, true,  isMC, blind, histDetailLevel, debug);
//  if(nTupleAnalysis::findSubStr(histDetailLevel,"passTTCR"))      passTTCR      = new   tagHists("passTTCR",      fs, true,  isMC, blind, histDetailLevel, debug);
//  if(nTupleAnalysis::findSubStr(histDetailLevel,"passTTCRe"))     passTTCRe     = new   tagHists("passTTCRe",     fs, true,  isMC, blind, histDetailLevel, debug);
//  if(nTupleAnalysis::findSubStr(histDetailLevel,"passTTCRem"))    passTTCRem    = new   tagHists("passTTCRem",    fs, true,  isMC, blind, histDetailLevel, debug);

  if(allEvents)     std::cout << "Turning on allEvents Hists" << std::endl; 
  if(Dimuon0_Jpsi)  std::cout << "Turning on Dimuon0_Jpsi Hists" << std::endl; 
  if(Dimuon25_Jpsi) std::cout << "Turning on Dimuon25_Jpsi Hists" << std::endl; 
  if(preSel)        std::cout << "Turning on preSel Hists" << std::endl; 
  if(bTags)         std::cout << "Turning on bTags Hists" << std::endl; 

//  if(pass4Jets)     std::cout << "Turning on pass4Jets Hists" << std::endl; 
//  if(pass4AllJets)  std::cout << "Turning on pass4AllJets Hists" << std::endl; 
//  //if(passDijetMass) std::cout << "Turning on passDijetMass Hists" << std::endl; 
//  // if(passMDRs)      std::cout << "Turning on passMDRs Hists" << std::endl; 
//  if(passSvB)       std::cout << "Turning on passSvB Hists" << std::endl; 
//  if(passMjjOth)    std::cout << "Turning on passMjjOth Hists" << std::endl; 
//  if(failrWbW2)     std::cout << "Turning on failrWbW2 Hists" << std::endl; 
//  if(passMuon)      std::cout << "Turning on passMuon Hists" << std::endl; 
//  if(passDvT05)     std::cout << "Turning on passDvT05 Hists" << std::endl; 
//  if(passTTCR)      std::cout << "Turning on passTTCR Hists" << std::endl; 
//  if(passTTCRe)     std::cout << "Turning on passTTCRe Hists" << std::endl; 
//  if(passTTCRem)    std::cout << "Turning on passTTCRem Hists" << std::endl; 
//

  histFile = &fs.file();
} 




void analysis::createPicoAOD(std::string fileName, bool copyInputPicoAOD){
  writePicoAOD = true;
  picoAODFile = TFile::Open(fileName.c_str() , "RECREATE");
  if(copyInputPicoAOD){
    //We are making a skim so we can directly clone the input TTree
    picoAODEvents = events->CloneTree(0);
  }else{
    //We are making a derived TTree which changes some of the branches of the input TTree so start from scratch
    picoAODEvents = new TTree("Events", "Events from Mixing");

    createPicoAODBranches();
  }
  addDerivedQuantitiesToPicoAOD();

  picoAODRuns       = runs      ->CloneTree();
  picoAODLumiBlocks = lumiBlocks->CloneTree();
}



void analysis::createPicoAODBranches(){
  cout << " analysis::createPicoAODBranches " << endl;

  //
  //  Initial Event Data
  //
  outputBranch(picoAODEvents, "run",               m_run, "i");
  outputBranch(picoAODEvents, "luminosityBlock",   m_lumiBlock,  "i");
  outputBranch(picoAODEvents, "event",             m_event,  "l");

  if(isMC){
    outputBranch(picoAODEvents, "genWeight",       m_genWeight,  "F");
    outputBranch(picoAODEvents, "bTagSF",          m_bTagSF,  "F");
  }

  
  outputBranch(picoAODEvents, "PV_npvs",         m_nPVs, "I");
  outputBranch(picoAODEvents, "PV_npvsGood",     m_nPVsGood, "I");
  outputBranch(picoAODEvents, "ttbarWeight",     m_ttbarWeight,  "F");

  //triggers
  for(auto &trigger: event-> L1_triggers) outputBranch(picoAODEvents, trigger.first, trigger.second, "O");
  for(auto &trigger: event->HLT_triggers) outputBranch(picoAODEvents, trigger.first, trigger.second, "O");
  //trigObjs = new trigData("TrigObj", tree);

}


void analysis::picoAODFillEvents(){
  if(debug) std::cout << "analysis::picoAODFillEvents()" << std::endl;
  if(alreadyFilled){
    if(debug) std::cout << "analysis::picoAODFillEvents() alreadyFilled" << std::endl;
    //std::cout << "ERROR: Filling picoAOD with same event twice" << std::endl;
    return;
  }
  alreadyFilled = true;

  if(debug) std::cout << "picoAODEvents->Fill()" << std::endl;
  picoAODEvents->Fill();  
  if(debug) std::cout << "analysis::picoAODFillEvents() done" << std::endl;
  return;
}



void analysis::addDerivedQuantitiesToPicoAOD(){
  cout << "analysis::addDerivedQuantitiesToPicoAOD()" << endl;
  if(fastSkim){
    cout<<"In fastSkim mode, skip adding derived quantities to picoAOD"<<endl;
    return;
  }
//
//  picoAODEvents->Branch("weight", &event->weight);
//  picoAODEvents->Branch("nPVsGood", &event->nPVsGood);
//  picoAODEvents->Branch("passHLT", &event->passHLT);

  cout << "analysis::addDerivedQuantitiesToPicoAOD() done" << endl;
  return;
}

void analysis::storePicoAOD(){
  picoAODFile->Write();
  picoAODFile->Close();
  return;
}


void analysis::monitor(long int e){
  //Monitor progress
  //timeTotal = ( std::clock() - start ) / (double) CLOCKS_PER_SEC;
  timeTotal = std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now() - start).count();
  timeElapsed          = timeTotal - previousMonitorTime;
  eventsElapsed        =         e - previousMonitorEvent;
  if( timeElapsed < 1 ) return;
  previousMonitorEvent = e;
  previousMonitorTime  = timeTotal;
  percent              = (e+1)*100/nEvents;
  eventRate            = eventRate ? 0.9*eventRate + 0.1*eventsElapsed/timeElapsed : eventsElapsed/timeElapsed; // Running average with 0.9 momentum
  timeRemaining        = (nEvents-e)/eventRate;
  //eventRate      = (e+1)/timeTotal;
  //timeRemaining  = (nEvents-e)/eventRate;
  hours   = static_cast<int>( timeRemaining/3600 );
  minutes = static_cast<int>( timeRemaining/60   )%60;
  seconds = static_cast<int>( timeRemaining      )%60;
  getrusage(who, &usage);
  usageMB = usage.ru_maxrss/1024;
  //print status and flush stdout so that status bar only uses one line
  if(isMC){
    fprintf(stdout, "\rProcessed: %9li of %9li ( %2li%% | %5.0f events/s | done in %02i:%02i:%02i | memory usage: %li MB)       ", 
	                          e+1, nEvents, percent,     eventRate,        hours, minutes, seconds,          usageMB);
  }else{
    fprintf(stdout, "\rProcessed: %9li of %9li ( %2li%% | %5.0f events/s | done in %02i:%02i:%02i | memory usage: %li MB | LumiBlocks %5i | Lumi %5.2f/fb [%3.0f%%, %3.0f%%: L1, HLT] )       ", 
	                          e+1, nEvents, percent,     eventRate,        hours, minutes, seconds,          usageMB,             nls,     intLumi/1000 , 100*intLumi_passL1/intLumi, 100*intLumi_passHLT/intLumi);    
  }
  fflush(stdout);
  return;
}

int analysis::eventLoop(int maxEvents, long int firstEvent){

  //Set Number of events to process. Take manual maxEvents if maxEvents is > 0 and less than the total number of events in the input files. 
  nEvents = (maxEvents > 0 && maxEvents < treeEvents) ? maxEvents : treeEvents;
  long int lastEvent = firstEvent + nEvents;
  
  cout << "\nProcess " << nEvents << " of " << treeEvents << " events.\n";
  if(firstEvent){
    cout << " \t... starting with  " <<  firstEvent << " \n";
    previousMonitorEvent = firstEvent;
  }


  //start = std::clock();
  start = std::chrono::system_clock::now();
  for(long int e = firstEvent; e < lastEvent; e++){
    
    currentEvent = e;

    alreadyFilled = false;

    event->update(e);    


    //
    //  Get the Data/MC Mixing 
    //

    if(writeOutEventNumbers){
      passed_runs  .push_back(event->eventDataTree->run);
      passed_events.push_back(event->eventDataTree->event);
      passed_LBs   .push_back(event->eventDataTree->luminosityBlock);
    }


    if(debug) cout << "processing event " << endl;    
    processEvent();
    if(debug) cout << "Done processing event " << endl;    
    //    if(debug) event->dump();
    if(debug) cout << "done " << endl;    

    //periodically update status
    monitor(e);
    if(debug) cout << "done loop " << endl;    
  }

  //std::cout<<"cutflow->labelsDeflate()"<<std::endl;
  //cutflow->labelsDeflate();

  //  lumiCounts->FillLumiBlock(intLumi - lumiLastWrite);

  cout << endl;
  if(!isMC){
    cout << "Runs " << firstRun << "-" << lastRun << endl;
  }

  eventRate = (nEvents)/timeTotal;

  hours   = static_cast<int>( timeTotal/3600 );
  minutes = static_cast<int>( timeTotal/60   )%60;
  seconds = static_cast<int>( timeTotal      )%60;
                                 
  if(isMC){
    fprintf(stdout,"---------------------------\nProcessed  %9li events in %02i:%02i:%02i (%5.0f events/s)",            nEvents, hours, minutes, seconds, eventRate);
  }else{
    fprintf(stdout,"---------------------------\nProcessed  %9li events in %02i:%02i:%02i (%5.0f events/s | %5.2f/fb)", nEvents, hours, minutes, seconds, eventRate, intLumi/1000);
  }
  return 0;
}

int analysis::processEvent(){
  if(debug) cout << "processEvent start" << endl;

//  if(isMC){
//    event->mcWeight = event->genWeight * (lumi * xs * kFactor / mcEventSumw);
//    if(!currentEvent) cout << "event->mcWeight = event->genWeight * (lumi * xs * kFactor / mcEventSumw) " << event->mcWeight 
//			   << " = " << event->genWeight << " * " << "(" << lumi << " * " << xs << " * " <<  kFactor <<" / " <<  mcEventSumw << ")" << endl;
//    if(event->nTrueBJets>=4) event->mcWeight *= fourbkfactor;
//    event->mcPseudoTagWeight = event->mcWeight * event->bTagSF * event->pseudoTagWeight * event->ttbarWeight * event->trigWeight;
//    event->weight *= event->mcWeight;
//    event->weightNoTrigger *= event->mcWeight;
//
//
//    if(debug){
//    std::cout << "Event: " << event->event << " Run: " << event->run << std::endl;
//    std::cout << "event->genWeight * (lumi * xs * kFactor / mcEventSumw) = " << std::endl;;
//      std::cout<< event->genWeight << " * (" << lumi << " * " << xs << " * " << kFactor << " / " << mcEventSumw << ") = " << event->mcWeight << std::endl;
//      std::cout<< "\tweight  " << event->weight << std::endl;
//      std::cout<< "\tbTagSF  " << event->bTagSF << std::endl;
//      std::cout<< "\tfourbkfactor " << fourbkfactor << std::endl;
//      std::cout<< "\tnTrueBJets " << event->nTrueBJets << std::endl;
//      std::cout<< "\tmcWeight " << event->mcWeight << std::endl;
//      std::cout<< "\tmcPseudoTagWeight " << event->mcPseudoTagWeight << std::endl;
//      std::cout<< "\tmcWeight " << event->mcWeight << std::endl;
//      std::cout<< "\tpseudoTagWeight " << event->pseudoTagWeight << std::endl;
//      std::cout<< "\treweight " << event->reweight << std::endl;
//      std::cout<< "\treweight4b " << event->reweight4b << std::endl;
//      std::cout<< "\ttrigWeight " << event->trigWeight << std::endl;
//      }
//
//
//  }

  if(debug) cout << "cutflow->Fill(event, all, true)" << endl;
  //  cutflow->Fill(event, "all", true);


  //  lumiCounts->Fill(event);



  //
  //if we are processing data, first apply lumiMask and trigger
  //
  bool isMCEvent = isMC;
  if(!isMCEvent){
    if(!passLumiMask()){
      if(debug) cout << "Fail lumiMask" << endl;
      return 0;
    }
    //cutflow->Fill(event, "lumiMask", true);

    //keep track of total lumi
    countLumi();

    if( (intLumi - lumiLastWrite) > 500){
      //lumiCounts->FillLumiBlock(intLumi - lumiLastWrite);
      lumiLastWrite = intLumi;
    }

    if(!event->passHLT){
      if(debug) cout << "Fail HLT: data" << endl;
      return 0;
    }
    //cutflow->Fill(event, "HLT", true);
  }else{
    //if(currentEvent > 0 && (currentEvent % 10000) == 0) 
    //lumiCounts->FillLumiBlock(1.0);
  }

  bool passHLT_Dimuon0 = event->HLT_triggers["HLT_Dimuon0_Jpsi3p5_Muon2"];
  
  if(allEvents != NULL && event->passHLT) allEvents->Fill(event);
  if(Dimuon0_Jpsi != NULL && passHLT_Dimuon0) Dimuon0_Jpsi->Fill(event);
  if(Dimuon25_Jpsi != NULL && event->HLT_triggers["HLT_Dimuon25_Jpsi"])        Dimuon25_Jpsi->Fill(event);


  //
  //  Preselection
  //
  bool jetMultiplicity  = (event->selJets.size() >= 2);
  if(!jetMultiplicity){
    if(debug) cout << "Fail Jet Multiplicity" << endl;
    return 0;
  }
//  cutflow->Fill(event, "jetMultiplicity", true);

  bool muonMultiplicity = (event->preSelMuons.size() >= 2);
  if(!muonMultiplicity){
    if(debug) cout << "Fail Muon Multiplicity" << endl;
    return 0;
  }
//  cutflow->Fill(event, "muonMultiplicity", true);
  
  if(preSel != NULL && passHLT_Dimuon0) preSel->Fill(event);

  bool bTagMultiplicity = (event->tagJets.size() >= 2);
  if(!bTagMultiplicity){
    if(debug) cout << "Fail bTag Multiplicity" << endl;
    return 0;
  }

  if(bTags != NULL && passHLT_Dimuon0) bTags->Fill(event);


  

  // Fill picoAOD
  if(writePicoAOD){
    picoAODFillEvents();
  }



   
  return 0;
}

bool analysis::passLumiMask(){
  // if the lumiMask is empty, then no JSON file was provided so all
  // events should pass
  if(lumiMask.empty()) return true;


  //make lumiID run:lumiBlock
  edm::LuminosityBlockID lumiID(event->eventDataTree->run, event->eventDataTree->luminosityBlock);

  //define function that checks if a lumiID is contained in a lumiBlockRange
  bool (*funcPtr) (edm::LuminosityBlockRange const &, edm::LuminosityBlockID const &) = &edm::contains;

  //Loop over the lumiMask and use funcPtr to check for a match
  std::vector< edm::LuminosityBlockRange >::const_iterator iter = std::find_if (lumiMask.begin(), lumiMask.end(), boost::bind(funcPtr, _1, lumiID) );

  return lumiMask.end() != iter; 
}

void analysis::getLumiData(std::string fileName){
  cout << "Getting integrated luminosity estimate per lumiBlock from: " << fileName << endl;
  brilCSV brilFile(fileName);
  lumiData = brilFile.GetData();
}

void analysis::countLumi(){
  edm::LuminosityBlockID lumiID(event->eventDataTree->run, event->eventDataTree->luminosityBlock);
  if(lumiID != prevLumiID){
  
    if(debug) std::cout << lumiID << " " << lumiData[lumiID] << " " << intLumi << " \n";

    // this is a new lumi block, count it
    lumiID_intLumi = lumiData[lumiID]; // units are /pb
    lumiData[lumiID] = 0;
    intLumi += lumiID_intLumi; // keep track of integrated luminosity
    nls     += 1;              // count number of lumi sections

    // set previous lumi block to this one
    prevLumiID = lumiID;

    // keep track of first and last run observed
    if(event->eventDataTree->run < firstRun) firstRun = event->eventDataTree->run;
    if(event->eventDataTree->run >  lastRun)  lastRun = event->eventDataTree->run;

    lumiID_passL1  = false;
    lumiID_passHLT = false;
  }
  if(!lumiID_passL1  && event->passL1 ){
    intLumi_passL1  += lumiID_intLumi; // keep track of integrated luminosity that passes trigger (expect ~100% of lumiblocks that pass lumi mask to have some events passing the trigger)
    lumiID_passL1  = true; // prevent counting this lumi block more than once
  }
  if(!lumiID_passHLT && event->passHLT){
    intLumi_passHLT += lumiID_intLumi; // keep track of integrated luminosity that passes trigger (expect ~100% of lumiblocks that pass lumi mask to have some events passing the trigger)
    lumiID_passHLT = true; // prevent counting this lumi block more than once
  }

  return;
}





analysis::~analysis(){

  if(writeOutEventNumbers){
    cout << "Writing out event Numbers" << endl;
    histFile->WriteObject(&passed_events, "passed_events"); 
    histFile->WriteObject(&passed_runs,   "passed_runs"); 
    histFile->WriteObject(&passed_LBs,    "passed_LBs"); 
  }
} 

