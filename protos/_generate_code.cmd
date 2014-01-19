
:: The StartOfTournament object...
protoc -I=. --python_out=. StartOfTournament.proto
protogen -i:StartOfTournament.proto -o:StartOfTournament.cs

