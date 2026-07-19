package main
import (
	"fmt"
	"github.com/mholt/archiver/v3"
)
func main() {
	err := archiver.Walk("test.zip", func(f archiver.File) error { return nil })
	fmt.Println(err)
}
