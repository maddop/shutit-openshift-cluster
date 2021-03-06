def do_controller(s):
	s.send('go version')
	s.send('go env')
	s.send('go get k8s.io/sample-controller')
	s.send('cd ${GOPATH}/src/k8s.io/sample-controller')
	# Build crd
	s.send('kubectl apply -f artifacts/examples/crd-validation.yaml')
	# Build the controller.
	s.send('go build -o ctrl .')
	s.send('nohup ./sample-controller -kubeconfig ~/.kube/config -logtostderr=true &')
	s.send('kubectl apply -f artifacts/examples/example-foo.yaml')
	s.pause_point('kubectl get pods')

	s.pause_point('next, try: https://itnext.io/building-an-operator-for-kubernetes-with-kubebuilder-17cbd3f07761')

	# Following: https://itnext.io/building-an-operator-for-kubernetes-with-the-sample-controller-b4204be9ad56
	s.send('mkdir -p artifacts/generic-daemon')
	s.send('''cat >  artifacts/generic-daemon/crd.yaml <<END
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: genericdaemons.mydomain.com
spec:
  group: mydomain.com
  version: v1beta1
  names:
    kind: Genericdaemon
    plural: genericdaemons
  scope: Namespaced
  validation:
    openAPIV3Schema:
      properties:
        spec:
          properties:
            label:
              type: string
            image:
              type: string
          required:
            - image
END''')
	s.send('''cat > artifacts/generic-daemon/syslog.yaml <<END
apiVersion: mydomain.com/v1beta1
kind: Genericdaemon
metadata:
  name: syslog
spec:
  label: logs
  image: mbessler/syslogdocker
END''')
	s.send('kubectl apply -f artifacts/generic-daemon/crd.yaml')
	s.send('kubectl apply -f artifacts/generic-daemon/syslog.yaml')
	s.send('mkdir -p pkg/apis/genericdaemon/v1beta1')
	s.send('cp pkg/apis/samplecontroller/register.go pkg/apis/genericdaemon')
	s.send('cp pkg/apis/samplecontroller/v1alpha1/{doc,register,types}.go pkg/apis/genericdaemon/v1beta1')
	s.send('''cat > pkg/apis/genericdaemon/register.go << END
package genericdaemon
const (
 GroupName = "mydomain.com"
)
END''')
	s.send('''cat > pkg/apis/genericdaemon/v1beta1/doc.go << END
// +k8s:deepcopy-gen=package
// Package v1beta1 is the v1beta1 version of the API.
// +groupName=mydomain.com
package v1beta1
END''')
	s.send('''cat > pks/apis/genericdaemon/v1beta1/register.go << END
package v1beta1
import (
 metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
 "k8s.io/apimachinery/pkg/runtime"
 "k8s.io/apimachinery/pkg/runtime/schema"
genericdaemon "k8s.io/sample-controller/pkg/apis/genericdaemon"
)
// SchemeGroupVersion is group version used to register these objects
var SchemeGroupVersion = schema.GroupVersion{Group: genericdaemon.GroupName, Version: "v1beta1"}
// Kind takes an unqualified kind and returns back a Group qualified GroupKind
func Kind(kind string) schema.GroupKind {
 return SchemeGroupVersion.WithKind(kind).GroupKind()
}
// Resource takes an unqualified resource and returns a Group qualified GroupResource
func Resource(resource string) schema.GroupResource {
 return SchemeGroupVersion.WithResource(resource).GroupResource()
}
var (
 SchemeBuilder = runtime.NewSchemeBuilder(addKnownTypes)
 AddToScheme   = SchemeBuilder.AddToScheme
)
// Adds the list of known types to Scheme.
func addKnownTypes(scheme *runtime.Scheme) error {
 scheme.AddKnownTypes(SchemeGroupVersion,
  &Genericdaemon{},
  &GenericdaemonList{},
 )
 metav1.AddToGroupVersion(scheme, SchemeGroupVersion)
 return nil
}
END''')
	s.send('''cat > pks/apis/genericdaemon/v1beta1/types.go << END

//////////////////////
// v1beta1/types.go
//////////////////////
package v1beta1
import (
 metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)
// +genclient
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
// Genericdaemon is a specification for a Generic Daemon resource
type Genericdaemon struct {
 metav1.TypeMeta   `json:",inline"`
 metav1.ObjectMeta `json:"metadata,omitempty"`
 Spec   GenericdaemonSpec   `json:"spec"`
 Status GenericdaemonStatus `json:"status"`
}
// GenericDaemonSpec is the spec for a GenericDaemon resource
type GenericdaemonSpec struct {
 Label string `json:"label"`
 Image string `json:"image"`
}
// GenericDaemonStatus is the status for a GenericDaemon resource
type GenericdaemonStatus struct {
 Installed int32 `json:"installed"`
}
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
// GenericDaemonList is a list of GenericDaemon resources
type GenericdaemonList struct {
 metav1.TypeMeta `json:",inline"`
 metav1.ListMeta `json:"metadata"`
Items []Genericdaemon `json:"items"`
}
END''')
	s.send('''cat > hack/update-codegen.sh << 'END'
#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
SCRIPT_ROOT=$(dirname ${BASH_SOURCE})/..
CODEGEN_PKG=${CODEGEN_PKG:-$(cd ${SCRIPT_ROOT}; ls -d -1 ./vendor/k8s.io/code-generator 2>/dev/null || echo ../code-generator)}
# generate the code with:
# --output-base    because this script should also be able to run inside the vendor dir of
#                  k8s.io/kubernetes. The output-base is needed for the generators to output into the vendor dir
#                  instead of the $GOPATH directly. For normal projects this can be dropped.
${CODEGEN_PKG}/generate-groups.sh "deepcopy,client,informer,lister" \
  k8s.io/sample-controller/pkg/client k8s.io/sample-controller/pkg/apis \
  genericdaemon:v1beta1 \
  --output-base "$(dirname ${BASH_SOURCE})/../../.." \
  --go-header-file ${SCRIPT_ROOT}/hack/boilerplate.go.txt
END''')
	s.send('''./hack/update-codegen.sh''')

#=========================================
## Does not work from here...
#cat > Dockerfile << END
#FROM golang
#RUN mkdir -p /go/src/k8s.io/sample-controller
#ADD . /go/src/k8s.io/sample-controller
#WORKDIR /go
#RUN go get ./...
#RUN go install -v ./...
#CMD ["/go/bin/sample-controller"]
#END
#docker build . -t docker.io/imiell/genericdaemon
#docker push docker.io/imiell/genericdaemon
#
#cat > deploy.yaml <<END
#apiVersion: apps/v1beta1
#kind: Deployment
#metadata:
#  name: sample-controller
#spec:
#  replicas: 1
#  selector:
#    matchLabels:
#      app: sample
#  template:
#    metadata:
#      labels:
#        app: sample
#    spec:
#      containers:
#      - name: sample
#        image: "imiell/genericdaemon:latest"
#END
#kubectl apply -f deploy.yaml
#=========================================


	# KUBEBUILDER
	# Read this: https://itnext.io/building-an-operator-for-kubernetes-with-kubebuilder-17cbd3f07761
	# From: https://book.kubebuilder.io/quick_start.html
	s.send('version=1.0.4 # latest stable version')
	s.send('arch=amd64')
	s.send('curl -L -O https://github.com/kubernetes-sigs/kubebuilder/releases/download/v${version}/kubebuilder_${version}_darwin_${arch}.tar.gz')
	s.send('tar -zxvf kubebuilder_${version}_darwin_${arch}.tar.gz')
	s.send('mv kubebuilder_${version}_darwin_${arch} /usr/local/kubebuilder')
	s.send('export PATH=$PATH:/usr/local/kubebuilder/bin')
	# Now start from article above:
	s.send('mkdir -p $GOPATH/src/mydomain.com/mygroup && cd $_')
	s.multisend('kubebuilder init --domain mydomain.com',{'dep ensure':'y'})
	# Go from here: Write some code / We need to modify the structure of our GenericDaemon to add the necessary fields for our object. Don't forget to document the fields, so the doc generator can create a good documentation:




	# Finally, operator SDK
	# https://itnext.io/building-an-operator-for-kubernetes-with-operator-sdk-40a029ea056
	s.send('go get github.com/operator-framework/operator-sdk')
	s.send('cd $GOPATH/src/github.com/operator-framework/operator-sdk')
	s.send('make dep')
	s.send('make install')
	s.send('mkdir -p $GOPATH/src/mydomain.com/mygroup2 && cd $_')
	s.send('operator-sdk new app-operator --api-version=mygroup2.mydomain.com/v1beta1 --kind=GenericDaemon')
	# Go from here: Write some code/ We need to modify the structure of our GenericDaemon to add the necessary fields for our object.
