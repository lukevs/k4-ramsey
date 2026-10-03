#define main original_engine_main
#include "../relation_engine/engine_v2.cpp"
#undef main
int main(int argc,char**argv){if(argc!=3)return 2;auto f=read_fixture(argv[1]);uint64_t mass;auto rows=census(f,mass);std::ofstream o(argv[2]);o<<mass<<" "<<rows.size()<<"\n";for(auto const&r:rows){o<<r.count;for(auto id:r.k.x)o<<" "<<id;o<<"\n";}return 0;}
