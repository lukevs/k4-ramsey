#define main archived_search_main
#include "search.cpp"
#undef main

struct BrokenResult {
  int r; long double start_density,continuous; int iterations; long double gradnorm;
  u128 red,blue,total,control; long double residual; int rounded_violations;
  std::vector<int> q;
};

std::vector<long double> broken_feature(const Group& G) {
  std::vector<long double> out(G.members.size());
  for(size_t o=0;o<G.members.size();o++) {
    long double sum=0;
    for(int g:G.members[o]) {auto [v,t]=G.decode(g);sum += ((v&1)?-1:1);}
    out[o]=sum/G.members[o].size();
  }
  return out;
}

std::pair<long double,int> invariance_residual(const Group& G,const std::vector<long double>& p,const std::vector<int>& q) {
  long double residual=0;int violations=0;
  for(int g=0;g<G.n;g++) {auto [v,t]=G.decode(g);int ag=G.code(G.apply(v,1),t);
    residual=std::max(residual,fabsl(p[G.orbit[g]]-p[G.orbit[ag]]));
    violations += q[G.orbit[g]]!=q[G.orbit[ag]];
  }
  return {residual,violations};
}

int main(int argc,char**argv) {
  if(argc!=2){std::cerr<<"usage: symmetry_breaking OUT\n";return 2;}
  tiny_oracle();auto started=std::chrono::steady_clock::now();
  const std::string control_strings[4]={"","16900975846882693440446359118219264","16901897597695656655017624392139328","17474320030049380006306612082900992"};
  auto parse128=[](const std::string&s){u128 x=0;for(char c:s)x=x*10+(c-'0');return x;};
  std::vector<BrokenResult> results;u128 best=~u128(0);int bestidx=-1;
  for(int r=1;r<=3;r++) {
    Group G(r);auto rows=rows_for(G);auto base=features(G,2),broken=broken_feature(G);std::vector<long double> p(base.size());
    for(size_t i=0;i<p.size();i++)p[i]=sigmoid(3*base[i]+2.5L*broken[i]);
    auto start_density=evaluate(rows,p,false).f;auto opt=optimize("nonclass_matrix_coefficient",rows,p,120);
    std::vector<int> q(opt.p.size());for(size_t i=0;i<q.size();i++)q[i]=std::clamp(int(llround(opt.p[i]*Q)),0,Q);
    auto [red,blue]=exact_count(rows,q);auto residual=invariance_residual(G,opt.p,q);u128 total=red+blue,control=parse128(control_strings[r]);
    results.push_back({r,start_density,opt.f,opt.iterations,opt.gradnorm,red,blue,total,control,residual.first,residual.second,q});
    if(total<best){best=total;bestidx=results.size()-1;}
  }
  auto& winner=results[bestidx];Group G(winner.r);fs::path out=argv[1];fs::create_directories(out);
  fs::copy_file("research/experiments/nonabelian_graphon/search.cpp",out/"search_dependency_snapshot.cpp",fs::copy_options::overwrite_existing);
  fs::copy_file("research/experiments/nonabelian_graphon/symmetry_breaking.cpp",out/"source_snapshot.cpp",fs::copy_options::overwrite_existing);
  fs::copy_file("research/experiments/nonabelian_graphon/symmetry_breaking_preregistration.json",out/"preregistration.json",fs::copy_options::overwrite_existing);
  std::ofstream cand(out/"graphon-candidate.json");cand<<"{\n  \"schema\": \"rational-step-graphon-v1\",\n  \"block_weights\": [";for(int i=0;i<192;i++){if(i)cand<<",";cand<<1;}cand<<"],\n  \"edge_probability_denominator\": "<<Q<<",\n  \"red_probability_numerators\": [\n";
  for(int i=0;i<192;i++){cand<<"    [";for(int j=0;j<192;j++){if(j)cand<<",";cand<<winner.q[G.orbit[G.diff(i,j)]];}cand<<"]"<<(i==191?"\n":",\n");}cand<<"  ]\n}\n";
  u128 den=u128(192)*192*192*ipow(Q,6),gg=gcd128(winner.total,den);auto elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();
  std::ofstream rep(out/"report.json");rep<<std::setprecision(18)<<"{\n  \"schema\": \"nonabelian-cayley-symmetry-breaking-v1\",\n  \"hypothesis\": \"H-NAB-01C\",\n  \"tiny_noncommutative_oracle\": \"passed\",\n  \"results\": [\n";
  for(size_t i=0;i<results.size();i++){auto&x=results[i];rep<<"    {\"acted_blocks\":"<<x.r<<",\"start_density\":"<<double(x.start_density)<<",\"continuous_density\":"<<double(x.continuous)<<",\"iterations\":"<<x.iterations<<",\"gradient_norm\":"<<double(x.gradnorm)<<",\"exact_total\":\""<<u128s(x.total)<<"\",\"control_total\":\""<<u128s(x.control)<<"\",\"exact_improves_control\":"<<(x.total<x.control?"true":"false")<<",\"max_action_invariance_residual\":"<<double(x.residual)<<",\"rounded_action_invariance_violations\":"<<x.rounded_violations<<"}"<<(i+1==results.size()?"\n":",\n");}
  rep<<"  ],\n  \"winner_acted_blocks\": "<<winner.r<<",\n  \"winner_exact_density\": \""<<u128s(winner.total/gg)<<"/"<<u128s(den/gg)<<"\",\n  \"winner_joint_success\": "<<(winner.total<winner.control&&winner.rounded_violations>0?"true":"false")<<",\n  \"elapsed_seconds\": "<<elapsed<<",\n  \"scope\": \"One preregistered action-breaking matrix-coefficient start per exhaustive action type; no random/amplitude sweep or global claim.\"\n}\n";
  std::cout<<std::setprecision(18)<<"winner r="<<winner.r<<" exact="<<u128s(winner.total/gg)<<"/"<<u128s(den/gg)<<" residual="<<double(winner.residual)<<" violations="<<winner.rounded_violations<<" elapsed="<<elapsed<<"\n";
  return 0;
}
