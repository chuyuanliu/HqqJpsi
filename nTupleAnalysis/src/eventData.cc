#include "HqqJpsi//nTupleAnalysis/interface/eventData.h"

using namespace HqqJpsi;

using std::cout; using std::endl; 
using std::vector; using std::string;

// Sorting functions
bool sortPt(       std::shared_ptr<nTupleAnalysis::jet>       &lhs, std::shared_ptr<nTupleAnalysis::jet>       &rhs){ return (lhs->pt        > rhs->pt   );     } // put largest  pt    first in list
bool sortDeepFlavB(std::shared_ptr<nTupleAnalysis::jet>       &lhs, std::shared_ptr<nTupleAnalysis::jet>       &rhs){ return (lhs->deepFlavB > rhs->deepFlavB); } // put largest  deepB first in list
bool sortDimuonMJPsi(std::shared_ptr<nTupleAnalysis::dimuon>  &lhs, std::shared_ptr<nTupleAnalysis::dimuon>    &rhs){ return (fabs(lhs->m - nTupleAnalysis::mJpsi) < fabs(rhs->m - nTupleAnalysis::mJpsi)); } 

eventData::eventData(TChain* t, bool mc, std::string y, bool d, bool _fastSkim, std::string bjetSF, std::string btagVariations, std::string JECSyst){
  std::cout << "eventData::eventData()" << std::endl;
  tree  = t;
  isMC  = mc;
  year  = ::atof(y.c_str());
  debug = d;
  fastSkim = _fastSkim;


  //std::cout << "eventData::eventData() tree->Lookup(true)" << std::endl;
  //tree->Lookup(true);
  eventDataTree = new nTupleAnalysis::eventData("", tree, true, isMC);

//  std::cout << "eventData::eventData() tree->LoadTree(0)" << std::endl;
//  tree->LoadTree(0);




  //triggers https://twiki.cern.ch/twiki/bin/viewauth/CMS/HLTPathsRunIIList
  if(year==2016){

    HLT_triggers["HLT_QuadJet45_TripleBTagCSV_p087"] = false; 
    HLT_triggers["HLT_DoubleJet90_Double30_TripleBTagCSV_p087"] = false;
    HLT_triggers["HLT_DoubleJetsC100_DoubleBTagCSV_p014_DoublePFJetsC100MaxDeta1p6"] = false;

  }

  if(year==2017){

  }

  if(year==2018){

    HLT_triggers["HLT_Dimuon0_Jpsi3p5_Muon2"] = false;
    //HLT_triggers["HLT_Dimuon25_Jpsi_noCorrL1_v"] = false;
    HLT_triggers["HLT_Dimuon25_Jpsi"] = false;
  }

  for(auto &trigger:  L1_triggers)     inputBranch(tree, trigger.first, trigger.second);
  for(auto &trigger: HLT_triggers)     inputBranch(tree, trigger.first, trigger.second);
  //for(auto &trigger:  L1_triggers_mon){
  //  if(L1_triggers.find(trigger.first)!=L1_triggers.end()) continue; // don't initialize branch again!
  //  inputBranch(tree, trigger.first, trigger.second);
  //}


  std::cout << "eventData::eventData() Initialize jets" << std::endl;
  treeJets  = new  nTupleAnalysis::jetData(    "Jet", tree, true, isMC, "", "", bjetSF, btagVariations, JECSyst);
  std::cout << "eventData::eventData() Initialize muons" << std::endl;
  treeMuons = new nTupleAnalysis::muonData(   "Muon", tree, true, isMC);
  std::cout << "eventData::eventData() Initialize elecs" << std::endl;
  treeElecs = new nTupleAnalysis::elecData(   "Electron", tree, true, isMC);
  std::cout << "eventData::eventData() Initialize TrigObj" << std::endl;
  //treeTrig  = new trigData("TrigObj", tree);
} 




void eventData::resetEvent(){
  if(debug) std::cout<<"Reset eventData"<<std::endl;
  preSelDiMuons.clear();
  dimuonJetClose .reset();
  dimuonJetOther .reset();
  diJets.reset();
  passL1  = false;
  passHLT = false;
  bTagSF = 1;
  treeJets->resetSFs();
  nTrueBJets = 0;
}



void eventData::update(long int e){
  if(debug){
    std::cout<<"Get Entry "<<e<<std::endl;
    std::cout<<tree->GetCurrentFile()->GetName()<<std::endl;
    tree->Show(e);
  }

  // if(printCurrentFile && tree->GetCurrentFile()->GetName() != currentFile){
  //   currentFile = tree->GetCurrentFile()->GetName();
  //   std::cout<< std::endl << "Loading: " << currentFile << std::endl;
  // }

  Long64_t loadStatus = tree->LoadTree(e);
  if(loadStatus<0){
   std::cout << "Error "<<loadStatus<<" getting event "<<e<<std::endl; 
   return;
  }

  tree->GetEntry(e);
  if(debug) std::cout<<"Got Entry "<<e<<std::endl;


  //
  // Reset the derived data
  //
  resetEvent();

  if(truth) truth->update();

  //Objects from ntuple
  if(debug) std::cout << "Get Jets\n";
  //getJets(float ptMin = -1e6, float ptMax = 1e6, float etaMax = 1e6, bool clean = false, float tagMin = -1e6, std::string tagger = "CSVv2", bool antiTag = false, int puIdMin = 0);
  allJets = treeJets->getJets(20, 1e6, 1e6, false, -1e6, bTagger, false, puIdMin);

  if(debug) std::cout << "Get Muons\n";

  buildEvent();

  for(auto &trigger: HLT_triggers){
    ///bool pass_seed = boost::accumulate(HLT_L1_seeds[trigger.first] | boost::adaptors::map_values, false, [](bool pass, bool *seed){return pass||*seed;});//std::logical_or<bool>());
    //passL1  = passL1  || pass_seed;
    //passHLT = passHLT || (trigger.second && pass_seed);
    passHLT = passHLT || (trigger.second);
  }


  //
  // HACK for now
  //
  passHLT = true;
  
  if(debug) std::cout<<"eventData updated\n";
  return;
}

void eventData::buildEvent(){

  //
  // Select Jets
  //
  selJets        = treeJets->getJets(       allJets, jetPtMin,   1e6, jetEtaMax, doJetCleaning);
  std::sort(selJets.begin(),       selJets.end(),       sortDeepFlavB);

  looseTagJets   = treeJets->getJets(       selJets, jetPtMin,   1e6, jetEtaMax, doJetCleaning, bTag/2, bTagger);
  tagJets        = treeJets->getJets(  looseTagJets, jetPtMin,   1e6, jetEtaMax, doJetCleaning, bTag,   bTagger);
  antiTag        = treeJets->getJets(       selJets, jetPtMin,   1e6, jetEtaMax, doJetCleaning, bTag/2, bTagger, true); //boolean specifies antiTag=true, inverts tagging criteria


  //btag SF
  if(isMC){
    //for(auto &jet: selJets) bTagSF *= treeJets->getSF(jet->eta, jet->pt, jet->deepFlavB, jet->hadronFlavour);
    treeJets->updateSFs(selJets, debug);
    bTagSF = treeJets->m_btagSFs["central"];

    if(debug) std::cout << "eventData buildEvent bTagSF = " << bTagSF << std::endl;
    //weight *= bTagSF;
    for(auto &jet: allJets) nTrueBJets += jet->hadronFlavour == 5 ? 1 : 0;
  }
  
  //
  // Select Muons
  //
  allMuons         = treeMuons->getMuons();
  preSelMuons      = treeMuons->getMuons(3.0, 2.4, 5, false, -1);


  //
  //  Select Electrons
  //
  allElecs         = treeElecs->getElecs();

  //
  // muon to jet matching
  //
    
  // To plots
  //   dR when match
  //   dR when no match

  for(const nTupleAnalysis::muonPtr& muon : preSelMuons){

    float dRMin_notMatch = 99;

    for(const nTupleAnalysis::jetPtr& jet : selJets){

      if((muon->jetIdx != -1) && (muon->jetIdx == jet->jetIdx)){
	muon->matchedJet = jet;
      }else{
	float thisDr = muon->p.DeltaR(jet->p);
	if(thisDr < dRMin_notMatch) dRMin_notMatch = thisDr;
      }

    }
    muon->dR = dRMin_notMatch;
  }




  //allTrigJets = treeTrig->getTrigs(0,1e6,1);
  //std::cout << "L1 Jets size:: " << allTriggerJets.size() << std::endl;

  //
  //  Build Di-Muon pairs
  //
  buildDiMuons(preSelMuons,    preSelDiMuons);


  //
  // If Di-Jets 
  //
  if(selJets.size() > 1){
    diJets = std::make_shared<nTupleAnalysis::dijet>(nTupleAnalysis::dijet(selJets[0], selJets[1]));
  }

  //
  // If Di-Jets and di-Muons
  //
  if(selJets.size() > 1 && preSelDiMuons.size()){
    const nTupleAnalysis::dimuonPtr& jPsi = preSelDiMuons[0]; 

    if(diJets->lead->p.DeltaR(jPsi->p) < diJets->subl->p.DeltaR(jPsi->p)){
      dimuonJetClose = std::make_shared<dimuonjet>(dimuonjet(preSelDiMuons[0], diJets->lead));
      dimuonJetOther = std::make_shared<dimuonjet>(dimuonjet(preSelDiMuons[0], diJets->subl));
    }else{						     
      dimuonJetClose = std::make_shared<dimuonjet>(dimuonjet(preSelDiMuons[0], diJets->subl));
      dimuonJetOther = std::make_shared<dimuonjet>(dimuonjet(preSelDiMuons[0], diJets->lead));
    }


  }


  


  
  if(debug) std::cout<<"eventData buildEvent done\n";
  return;
}


void eventData::buildDiMuons(std::vector<nTupleAnalysis::muonPtr>& thisMuons, std::vector<nTupleAnalysis::dimuonPtr>& thisDiMuons){

  for(unsigned int iM = 0; iM < thisMuons.size(); ++iM){
    for(unsigned int jM = iM; jM < thisMuons.size(); ++jM){
      if(iM == jM) continue;
      if(debug) cout << "Creating dimuon " << iM << " " << jM << endl;
      //cout << "Creating dimuon " << iM << " " << jM << endl;
      thisDiMuons.push_back(std::make_shared<nTupleAnalysis::dimuon>(nTupleAnalysis::dimuon(thisMuons[iM], thisMuons[jM])));
    }
  }

  std::sort(thisDiMuons.begin(), thisDiMuons.end(), sortDimuonMJPsi);
}







void eventData::dump(){

  std::cout << "   Run: " << eventDataTree->run    << std::endl;
  std::cout << " Event: " << eventDataTree->event  << std::endl;  
  //std::cout << "Weight: " << eventDataTree->weight << std::endl;
  //std::cout << "Trigger Weight : " << trigWeight << std::endl;
  //std::cout << "WeightNoTrig: " << weightNoTrigger << std::endl;
  std::cout << " allJets: " << allJets .size() << " |  selJets: " << selJets .size() << " | tagJets: " << tagJets.size() << std::endl;
  std::cout << "allMuons: " << allMuons.size() << " | preSelMuons: " << preSelMuons.size() << std::endl;

  cout << "All Jets" << endl;
  for(auto& jet : allJets){
    std::cout << "\t " << jet->pt << " (" << jet->pt_wo_bRegCorr << ") " <<  jet->eta << " " << jet->phi << " " << jet->deepB  << " " << jet->deepFlavB << " " << (jet->pt - 40) << std::endl;
  }

  cout << "Sel Jets" << endl;
  for(auto& jet : selJets){
    std::cout << "\t " << jet->pt << " " << jet->eta << " " << jet->phi << " " << jet->deepB  << " " << jet->deepFlavB << std::endl;
  }

  cout << "Tag Jets" << endl;
  for(auto& jet : tagJets){
    std::cout << "\t " << jet->pt << " " << jet->eta << " " << jet->phi << " " << jet->deepB  << " " << jet->deepFlavB << std::endl;
  }


  return;
}

eventData::~eventData(){} 

