#define main archived_search_main
#include "search.cpp"
#undef main

#include <regex>

std::vector<int> read_numerators(const fs::path& path) {
  std::ifstream in(path); std::string text((std::istreambuf_iterator<char>(in)),{});
  auto pos=text.find("\"numerators\""); assert(pos!=std::string::npos);
  pos=text.find('[',pos); auto end=text.find(']',pos); assert(end!=std::string::npos);
  std::vector<int> values; std::regex number("[0-9]+");
  std::string body=text.substr(pos+1,end-pos-1);
  for(std::sregex_iterator it(body.begin(),body.end(),number),stop;it!=stop;++it)values.push_back(std::stoi(it->str()));
  return values;
}

int main(int argc,char**argv) {
  if(argc!=3){std::cerr<<"usage: continue_r1 INPUT_PROBS OUT\n";return 2;}
  tiny_oracle(); auto started=std::chrono::steady_clock::now(); Group G(1); auto rows=rows_for(G);
  auto initial_q=read_numerators(argv[1]); assert(initial_q.size()==G.members.size());
  std::vector<long double> initial(initial_q.size());for(size_t i=0;i<initial.size();i++)initial[i]=static_cast<long double>(initial_q[i])/Q;
  auto before=evaluate(rows,initial,false).f;
  auto opt=optimize("r1_invariant_quadratic_continuation",rows,initial,200);
  std::vector<int> q(opt.p.size());for(size_t i=0;i<q.size();i++)q[i]=std::clamp(int(llround(opt.p[i]*Q)),0,Q);
  auto [red,blue]=exact_count(rows,q);u128 total=red+blue,den=u128(192)*192*192*ipow(Q,6),gg=gcd128(total,den);
  fs::path out=argv[2];fs::create_directories(out);
  fs::copy_file("experiments/nonabelian_graphon/search.cpp",out/"search_dependency_snapshot.cpp",fs::copy_options::overwrite_existing);
  fs::copy_file("experiments/nonabelian_graphon/continue_r1.cpp",out/"source_snapshot.cpp",fs::copy_options::overwrite_existing);
  std::ofstream cand(out/"graphon-candidate.json");cand<<"{\n  \"schema\": \"rational-step-graphon-v1\",\n  \"block_weights\": [";for(int i=0;i<192;i++){if(i)cand<<",";cand<<1;}cand<<"],\n  \"edge_probability_denominator\": "<<Q<<",\n  \"red_probability_numerators\": [\n";
  bool symmetric=true,in_range=true;
  for(int i=0;i<192;i++){cand<<"    [";for(int j=0;j<192;j++){if(j)cand<<",";int x=q[G.orbit[G.diff(i,j)]];int y=q[G.orbit[G.diff(j,i)]];symmetric&=x==y;in_range&=0<=x&&x<=Q;cand<<x;}cand<<"]"<<(i==191?"\n":",\n");}cand<<"  ]\n}\n";
  assert(symmetric&&in_range);
  auto part=subgroup_partition(G,rows,opt.p);auto elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();
  std::ofstream rep(out/"report.json");rep<<std::setprecision(18)<<"{\n  \"schema\": \"nonabelian-cayley-r1-continuation-v1\",\n  \"hypothesis\": \"H-NAB-01B\",\n  \"control\": \"reports/nonabelian-cayley-001\",\n  \"initial_rounded_density\": "<<double(before)<<",\n  \"continuous_density\": "<<double(opt.f)<<",\n  \"iterations\": "<<opt.iterations<<",\n  \"gradient_norm\": "<<double(opt.gradnorm)<<",\n  \"exact_red\": \""<<u128s(red)<<"\",\n  \"exact_blue\": \""<<u128s(blue)<<"\",\n  \"exact_total\": \""<<u128s(total)<<"\",\n  \"exact_denominator\": \""<<u128s(den)<<"\",\n  \"exact_density\": \""<<u128s(total/gg)<<"/"<<u128s(den/gg)<<"\",\n  \"subspace_partition\": ["<<double(part.rank_le_2)<<","<<double(part.rank_3)<<","<<double(part.rest)<<"],\n  \"candidate_checks\": {\"symmetric\":true,\"probabilities_in_range\":true,\"inverse_orbits\":128},\n  \"elapsed_seconds\": "<<elapsed<<",\n  \"termination\": \"iteration_limit_or_gradient_stop\",\n  \"scope\": \"One deterministic continuation of the supported r=1 basin; no restart/global claim.\"\n}\n";
  std::ofstream probs(out/"inverse-orbit-probabilities.json");probs<<"{\n  \"acted_blocks\": 1,\n  \"denominator\": "<<Q<<",\n  \"numerators\": [";for(size_t i=0;i<q.size();i++){if(i)probs<<",";probs<<q[i];}probs<<"]\n}\n";
  std::cout<<std::setprecision(18)<<"before="<<double(before)<<" after="<<double(opt.f)<<" grad="<<double(opt.gradnorm)<<" exact="<<u128s(total/gg)<<"/"<<u128s(den/gg)<<" elapsed="<<elapsed<<"\n";
  return 0;
}
